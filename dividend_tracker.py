"""
Dividend Tracker for Investment Dashboard
Tracks dividend payments, calculates yields, and forecasts income
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import streamlit as st


class DividendTracker:
    """Track and analyze dividend payments from portfolio"""
    
    def __init__(self, portfolio_df: pd.DataFrame):
        """
        Initialize DividendTracker with portfolio data
        
        Args:
            portfolio_df: DataFrame with columns including Dividend, DivMonth, DivFrequency
        """
        self.portfolio_df = portfolio_df
        self.current_year = datetime.now().year
        
    def get_dividend_payers(self) -> pd.DataFrame:
        """Get only positions that pay dividends"""
        return self.portfolio_df[
            (self.portfolio_df['Dividend'].notna()) & 
            (self.portfolio_df['Dividend'] > 0)
        ].copy()
    
    def calculate_annual_dividend(self, row: pd.Series) -> float:
        """
        Calculate annual dividend for a position
        
        Args:
            row: Portfolio row with Dividend, DivFrequency, Quantity
            
        Returns:
            Annual dividend amount in EUR
        """
        dividend = row['Dividend']
        quantity = row['Quantity']
        frequency = row.get('DivFrequency', 'Annual')
        
        # Frequency multiplier
        freq_multiplier = {
            'Annual': 1,
            'SemiAnnual': 2,
            'Quarterly': 4,
            'Monthly': 12
        }.get(frequency, 1)
        
        annual_dividend = dividend * quantity * freq_multiplier
        
        return annual_dividend
    
    def calculate_yield_on_cost(self, row: pd.Series) -> float:
        """
        Calculate Yield on Cost (dividend yield on purchase price)
        
        Args:
            row: Portfolio row with Dividend, BuyPrice, DivFrequency
            
        Returns:
            YoC as percentage
        """
        dividend = row['Dividend']
        buy_price = row.get('BuyPrice', 0)
        frequency = row.get('DivFrequency', 'Annual')
        
        if buy_price == 0:
            return 0.0
        
        freq_multiplier = {
            'Annual': 1,
            'SemiAnnual': 2,
            'Quarterly': 4,
            'Monthly': 12
        }.get(frequency, 1)
        
        annual_dividend = dividend * freq_multiplier
        yoc = (annual_dividend / buy_price) * 100
        
        return yoc
    
    def get_next_payment_date(self, month: int, frequency: str) -> datetime:
        """
        Calculate next payment date based on month and frequency
        
        Args:
            month: Payment month (1-12)
            frequency: Payment frequency
            
        Returns:
            Next payment datetime
        """
        today = datetime.now()
        current_year = today.year
        
        # For quarterly/semiannual, find next payment month
        if frequency == 'Quarterly':
            # Payment months: month, month+3, month+6, month+9
            payment_months = [(month + i*3 - 1) % 12 + 1 for i in range(4)]
            next_months = [m for m in payment_months if m >= today.month or m < today.month]
            next_month = min(next_months) if next_months else payment_months[0]
            year = current_year if next_month >= today.month else current_year + 1
            
        elif frequency == 'SemiAnnual':
            # Payment months: month, month+6
            payment_months = [month, (month + 6 - 1) % 12 + 1]
            next_months = [m for m in payment_months if m >= today.month or m < today.month]
            next_month = min(next_months) if next_months else payment_months[0]
            year = current_year if next_month >= today.month else current_year + 1
            
        else:  # Annual
            next_month = month
            year = current_year if month >= today.month else current_year + 1
        
        # Estimate mid-month payment (15th)
        payment_date = datetime(year, next_month, 15)
        
        return payment_date
    
    def get_upcoming_payments(self, days_ahead: int = 90) -> pd.DataFrame:
        """
        Get upcoming dividend payments within specified days
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            DataFrame with upcoming payments sorted by date
        """
        div_payers = self.get_dividend_payers()
        
        if div_payers.empty:
            return pd.DataFrame()
        
        upcoming = []
        today = datetime.now()
        
        for _, row in div_payers.iterrows():
            month = int(row['DivMonth'])
            frequency = row.get('DivFrequency', 'Annual')
            
            payment_date = self.get_next_payment_date(month, frequency)
            days_until = (payment_date - today).days
            
            if 0 <= days_until <= days_ahead:
                annual_div = self.calculate_annual_dividend(row)
                yoc = self.calculate_yield_on_cost(row)
                
                # Calculate payment amount based on frequency
                freq_divisor = {
                    'Annual': 1,
                    'SemiAnnual': 2,
                    'Quarterly': 4,
                    'Monthly': 12
                }.get(frequency, 1)
                
                payment_amount = annual_div / freq_divisor
                
                upcoming.append({
                    'Ticker': row['Ticker'],
                    'Name': row['Name'],
                    'PaymentDate': payment_date,
                    'Amount': payment_amount,
                    'YoC': yoc,
                    'DaysUntil': days_until
                })
        
        if not upcoming:
            return pd.DataFrame()
        
        df = pd.DataFrame(upcoming)
        df = df.sort_values('PaymentDate')
        
        return df
    
    def get_total_annual_dividends(self) -> float:
        """Calculate total annual dividend income"""
        div_payers = self.get_dividend_payers()
        
        if div_payers.empty:
            return 0.0
        
        total = sum(self.calculate_annual_dividend(row) for _, row in div_payers.iterrows())
        
        return total
    
    def get_top_dividend_payers(self, n: int = 5) -> pd.DataFrame:
        """
        Get top N dividend payers by annual amount
        
        Args:
            n: Number of top payers to return
            
        Returns:
            DataFrame with top dividend payers
        """
        div_payers = self.get_dividend_payers()
        
        if div_payers.empty:
            return pd.DataFrame()
        
        top_payers = []
        
        for _, row in div_payers.iterrows():
            annual_div = self.calculate_annual_dividend(row)
            yoc = self.calculate_yield_on_cost(row)
            
            top_payers.append({
                'Ticker': row['Ticker'],
                'Name': row['Name'],
                'AnnualDividend': annual_div,
                'YoC': yoc
            })
        
        df = pd.DataFrame(top_payers)
        df = df.sort_values('AnnualDividend', ascending=False).head(n)
        
        return df
    
    def get_monthly_distribution(self) -> Dict[int, float]:
        """
        Get dividend distribution by month
        
        Returns:
            Dictionary with month number as key and total dividends as value
        """
        div_payers = self.get_dividend_payers()
        
        monthly = {i: 0.0 for i in range(1, 13)}
        
        for _, row in div_payers.iterrows():
            month = int(row['DivMonth'])
            frequency = row.get('DivFrequency', 'Annual')
            annual_div = self.calculate_annual_dividend(row)
            
            freq_divisor = {
                'Annual': 1,
                'SemiAnnual': 2,
                'Quarterly': 4,
                'Monthly': 12
            }.get(frequency, 1)
            
            payment_amount = annual_div / freq_divisor
            
            # Add to appropriate months based on frequency
            if frequency == 'Quarterly':
                for i in range(4):
                    payment_month = (month + i*3 - 1) % 12 + 1
                    monthly[payment_month] += payment_amount
                    
            elif frequency == 'SemiAnnual':
                monthly[month] += payment_amount
                monthly[(month + 6 - 1) % 12 + 1] += payment_amount
                
            else:  # Annual or Monthly
                monthly[month] += payment_amount
        
        return monthly
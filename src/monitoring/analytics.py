"""
Analytics module for Scene+ recommendation service.
"""
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class OfferAnalytics:
    """Analytics for offer performance."""
    
    def __init__(self, lookback_days: int = 30):
        """Initialize analytics with lookback period."""
        self.lookback_days = lookback_days
    
    def analyze_offer_performance(
        self,
        offer_events: pd.DataFrame,
        customer_segments: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyze offer performance metrics.
        
        Args:
            offer_events: DataFrame of offer events
            customer_segments: DataFrame of customer segments
            
        Returns:
            Dict containing performance metrics
        """
        # Filter events within lookback period
        cutoff_date = datetime.now() - timedelta(days=self.lookback_days)
        recent_events = offer_events[offer_events['timestamp'] >= cutoff_date]
        
        # Calculate conversion rates
        conversions = self._calculate_conversion_rates(recent_events)
        
        # Calculate segment performance
        segment_performance = self._analyze_segment_performance(
            recent_events,
            customer_segments
        )
        
        # Calculate offer type performance
        offer_type_performance = self._analyze_offer_types(recent_events)
        
        return {
            'conversion_rates': conversions,
            'segment_performance': segment_performance,
            'offer_type_performance': offer_type_performance,
            'time_period': {
                'start': cutoff_date.isoformat(),
                'end': datetime.now().isoformat(),
                'days': self.lookback_days
            }
        }
    
    def _calculate_conversion_rates(self, events: pd.DataFrame) -> Dict[str, float]:
        """Calculate conversion rates for different event types."""
        total_offers = len(events[events['event_type'] == 'generate'])
        if total_offers == 0:
            return {}
        
        return {
            'view_rate': len(events[events['event_type'] == 'view']) / total_offers,
            'click_rate': len(events[events['event_type'] == 'click']) / total_offers,
            'redemption_rate': len(events[events['event_type'] == 'redeem']) / total_offers
        }
    
    def _analyze_segment_performance(
        self,
        events: pd.DataFrame,
        segments: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """Analyze performance by customer segment."""
        merged_data = pd.merge(
            events,
            segments,
            on='customer_id',
            how='left'
        )
        
        performance = {}
        for segment in segments['segment'].unique():
            segment_events = merged_data[merged_data['segment'] == segment]
            
            if len(segment_events) > 0:
                performance[segment] = {
                    'offer_count': len(segment_events[segment_events['event_type'] == 'generate']),
                    'view_rate': len(segment_events[segment_events['event_type'] == 'view']) / len(segment_events),
                    'redemption_rate': len(segment_events[segment_events['event_type'] == 'redeem']) / len(segment_events),
                    'average_value': segment_events['offer_value'].mean()
                }
        
        return performance
    
    def _analyze_offer_types(self, events: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Analyze performance by offer type."""
        performance = {}
        for offer_type in events['offer_type'].unique():
            type_events = events[events['offer_type'] == offer_type]
            
            if len(type_events) > 0:
                performance[offer_type] = {
                    'count': len(type_events[type_events['event_type'] == 'generate']),
                    'view_rate': len(type_events[type_events['event_type'] == 'view']) / len(type_events),
                    'redemption_rate': len(type_events[type_events['event_type'] == 'redeem']) / len(type_events),
                    'average_value': type_events['offer_value'].mean()
                }
        
        return performance


class PerformanceAnalytics:
    """Analytics for system performance."""
    
    def analyze_api_performance(
        self,
        request_metrics: pd.DataFrame,
        error_threshold_ms: float = 500
    ) -> Dict[str, Any]:
        """
        Analyze API performance metrics.
        
        Args:
            request_metrics: DataFrame of API request metrics
            error_threshold_ms: Latency threshold for errors (milliseconds)
            
        Returns:
            Dict containing performance metrics
        """
        performance = {
            'request_count': len(request_metrics),
            'error_rate': len(request_metrics[request_metrics['status'] >= 400]) / len(request_metrics),
            'latency': {
                'p50': request_metrics['latency'].quantile(0.5),
                'p90': request_metrics['latency'].quantile(0.9),
                'p99': request_metrics['latency'].quantile(0.99)
            },
            'endpoints': {}
        }
        
        # Analyze performance by endpoint
        for endpoint in request_metrics['endpoint'].unique():
            endpoint_data = request_metrics[request_metrics['endpoint'] == endpoint]
            
            performance['endpoints'][endpoint] = {
                'request_count': len(endpoint_data),
                'error_rate': len(endpoint_data[endpoint_data['status'] >= 400]) / len(endpoint_data),
                'average_latency': endpoint_data['latency'].mean(),
                'slow_requests': len(endpoint_data[endpoint_data['latency'] > error_threshold_ms])
            }
        
        return performance
    
    def analyze_model_performance(
        self,
        prediction_metrics: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze model prediction performance.
        
        Args:
            prediction_metrics: DataFrame of model prediction metrics
            
        Returns:
            Dict containing model performance metrics
        """
        performance = {}
        for model in prediction_metrics['model_name'].unique():
            model_data = prediction_metrics[prediction_metrics['model_name'] == model]
            
            performance[model] = {
                'prediction_count': len(model_data),
                'average_latency': model_data['latency'].mean(),
                'p95_latency': model_data['latency'].quantile(0.95),
                'max_latency': model_data['latency'].max()
            }
        
        return performance


class CustomerAnalytics:
    """Analytics for customer behavior."""
    
    def analyze_customer_engagement(
        self,
        customer_events: pd.DataFrame,
        segments: pd.DataFrame,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze customer engagement metrics.
        
        Args:
            customer_events: DataFrame of customer events
            segments: DataFrame of customer segments
            lookback_days: Number of days to analyze
            
        Returns:
            Dict containing engagement metrics
        """
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        recent_events = customer_events[customer_events['timestamp'] >= cutoff_date]
        
        # Merge with segments
        merged_data = pd.merge(
            recent_events,
            segments,
            on='customer_id',
            how='left'
        )
        
        engagement = {
            'active_customers': len(merged_data['customer_id'].unique()),
            'events_per_customer': len(recent_events) / len(merged_data['customer_id'].unique()),
            'segment_engagement': self._analyze_segment_engagement(merged_data),
            'time_series': self._create_engagement_timeseries(merged_data)
        }
        
        return engagement
    
    def _analyze_segment_engagement(self, events: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Analyze engagement metrics by segment."""
        engagement = {}
        for segment in events['segment'].unique():
            segment_events = events[events['segment'] == segment]
            
            engagement[segment] = {
                'customer_count': len(segment_events['customer_id'].unique()),
                'events_per_customer': len(segment_events) / len(segment_events['customer_id'].unique()),
                'average_points_balance': segment_events['points_balance'].mean(),
                'active_percentage': len(segment_events[segment_events['days_since_last_activity'] <= 30]) / len(segment_events)
            }
        
        return engagement
    
    def _create_engagement_timeseries(self, events: pd.DataFrame) -> Dict[str, List[float]]:
        """Create time series of engagement metrics."""
        daily_metrics = events.groupby(pd.Grouper(key='timestamp', freq='D')).agg({
            'customer_id': 'nunique',
            'event_type': 'count',
            'points_balance': 'mean'
        }).reset_index()
        
        return {
            'dates': daily_metrics['timestamp'].dt.strftime('%Y-%m-%d').tolist(),
            'active_customers': daily_metrics['customer_id'].tolist(),
            'event_count': daily_metrics['event_type'].tolist(),
            'average_points': daily_metrics['points_balance'].tolist()
        }


def generate_analytics_report(
    offer_analytics: Dict[str, Any],
    performance_analytics: Dict[str, Any],
    customer_analytics: Dict[str, Any],
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a comprehensive analytics report.
    
    Args:
        offer_analytics: Offer performance metrics
        performance_analytics: System performance metrics
        customer_analytics: Customer engagement metrics
        output_file: Optional file to save report
        
    Returns:
        Dict containing the complete analytics report
    """
    report = {
        'generated_at': datetime.now().isoformat(),
        'offer_performance': offer_analytics,
        'system_performance': performance_analytics,
        'customer_engagement': customer_analytics,
        'summary': {
            'total_offers': sum(
                segment['offer_count']
                for segment in offer_analytics['segment_performance'].values()
            ),
            'active_customers': customer_analytics['active_customers'],
            'overall_redemption_rate': offer_analytics['conversion_rates'].get('redemption_rate', 0),
            'system_error_rate': performance_analytics['error_rate']
        }
    }
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    return report 
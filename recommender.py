"""
Rule-Based Expert System for Personalized Running Recommendations
Uses cluster profiles and athlete metrics to generate training advice
"""

import json
from pathlib import Path


class RunningRecommender:
    """
    Expert system that provides personalized training recommendations
    based on athlete cluster, current metrics, and goals.
    """
    
    def __init__(self, cluster_profiles_path='data/cluster_profiles.json'):
        """
        Initialize the recommender with cluster profiles.
        
        Args:
            cluster_profiles_path: Path to cluster_profiles.json file
        """
        self.cluster_profiles = self._load_cluster_profiles(cluster_profiles_path)
        
    def _load_cluster_profiles(self, path):
        """Load cluster profiles from JSON file."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def get_cluster_name(self, cluster_id):
        """Get the human-readable name for a cluster."""
        cluster_map = {
            0: "Foundation Builder",
            1: "Consistent Cruiser", 
            2: "Competitive Peak"
        }
        return cluster_map.get(cluster_id, "Unknown")
    
    def get_recommendation(self, 
                          cluster_id,
                          current_weekly_mileage,
                          predicted_next_week_mileage,
                          current_fatigue_index,
                          training_days_per_week,
                          goal_race_distance=None,
                          weeks_until_race=None):
        """
        Generate personalized training recommendation.
        
        Args:
            cluster_id: 0 (Foundation), 1 (Cruiser), or 2 (Peak)
            current_weekly_mileage: Current week's total mileage
            predicted_next_week_mileage: LSTM prediction for next week
            current_fatigue_index: Current fatigue score
            training_days_per_week: Number of training days per week
            goal_race_distance: Optional race distance in miles (5K=3.1, 10K=6.2, Half=13.1, Full=26.2)
            weeks_until_race: Optional weeks until goal race
            
        Returns:
            Dictionary with recommendation details
        """
        
        # Get cluster profile
        cluster_profile = self.cluster_profiles[str(cluster_id)]
        cluster_name = self.get_cluster_name(cluster_id)
        
        # Calculate mileage change
        mileage_change = predicted_next_week_mileage - current_weekly_mileage
        mileage_change_pct = (mileage_change / current_weekly_mileage * 100) if current_weekly_mileage > 0 else 0
        
        # Initialize recommendation structure
        recommendation = {
            "cluster_id": cluster_id,
            "cluster_name": cluster_name,
            "current_mileage": current_weekly_mileage,
            "predicted_mileage": predicted_next_week_mileage,
            "mileage_change": mileage_change,
            "mileage_change_pct": mileage_change_pct,
            "current_fatigue": current_fatigue_index,
            "training_days": training_days_per_week,
            "action": None,
            "volume_recommendation": None,
            "intensity_focus": None,
            "recovery_advice": None,
            "weekly_structure": None,
            "caution_flags": []
        }
        
        # Apply cluster-specific rules
        if cluster_id == 0:  # Foundation Builder
            recommendation = self._foundation_builder_rules(recommendation, 
                                                            current_fatigue_index,
                                                            training_days_per_week,
                                                            mileage_change_pct)
        
        elif cluster_id == 1:  # Consistent Cruiser
            recommendation = self._consistent_cruiser_rules(recommendation,
                                                           current_fatigue_index,
                                                           current_weekly_mileage,
                                                           mileage_change_pct)
        
        elif cluster_id == 2:  # Competitive Peak
            recommendation = self._competitive_peak_rules(recommendation,
                                                         current_fatigue_index,
                                                         current_weekly_mileage,
                                                         mileage_change_pct,
                                                         weeks_until_race)
        
        # Apply race-specific adjustments if goal race provided
        if goal_race_distance and weeks_until_race:
            recommendation = self._apply_race_adjustments(recommendation,
                                                          goal_race_distance,
                                                          weeks_until_race)
        
        return recommendation
    
    def _foundation_builder_rules(self, rec, fatigue, training_days, mileage_change_pct):
        """Rules for Foundation Builder cluster (Cluster 0)."""
        
        # Check training frequency
        if training_days < 3:
            rec["action"] = "build_consistency"
            rec["volume_recommendation"] = "Maintain current volume, focus on adding 1 more training day"
            rec["caution_flags"].append("Training frequency below 3 days/week - prioritize consistency")
        
        # Check for overtraining
        elif fatigue > 20:
            rec["action"] = "recovery_focus"
            rec["volume_recommendation"] = "Reduce mileage by 10-15% this week"
            rec["caution_flags"].append("Elevated fatigue for beginner level - add recovery day")
        
        # Check for excessive mileage increase
        elif mileage_change_pct > 15:
            rec["action"] = "slow_progression"
            rec["volume_recommendation"] = "Cap increase to 10% per week to avoid injury"
            rec["caution_flags"].append("Predicted increase exceeds 10% rule - risk of overuse injury")
        
        # Normal progression
        else:
            rec["action"] = "gradual_build"
            rec["volume_recommendation"] = "Increase mileage by 5-10% (0.5-1 mile)"
        
        # Standard Foundation Builder advice
        rec["intensity_focus"] = "Easy pace only - focus on time on feet, not speed"
        rec["recovery_advice"] = "Take at least 2 full rest days. Prioritize sleep and nutrition."
        rec["weekly_structure"] = """
        Suggested Week:
        • 3-4 easy runs (20-30 min each)
        • 1 longer easy run (gradually build to 40-60 min)
        • 2-3 complete rest days
        • Optional: 1-2 days of light cross-training (walking, cycling)
        """
        
        return rec
    
    def _consistent_cruiser_rules(self, rec, fatigue, mileage, mileage_change_pct):
        """Rules for Consistent Cruiser cluster (Cluster 1)."""
        
        # Check fatigue level
        if fatigue > 30:
            rec["action"] = "recovery_week"
            rec["volume_recommendation"] = "Reduce mileage by 20% for recovery"
            rec["caution_flags"].append("High fatigue - implement recovery week")
        
        # Check for stagnation
        elif abs(mileage_change_pct) < 2 and mileage < 25:
            rec["action"] = "progressive_overload"
            rec["volume_recommendation"] = "Increase mileage by 10% (2-3 miles) to continue progression"
        
        # Check for excessive increase
        elif mileage_change_pct > 12:
            rec["action"] = "moderate_increase"
            rec["volume_recommendation"] = "Cap increase to 10-12% to balance progression and recovery"
            rec["caution_flags"].append("Predicted increase high - moderate to safer level")
        
        # Normal progression
        else:
            rec["action"] = "balanced_progression"
            rec["volume_recommendation"] = "Increase mileage by 8-10% (1.5-2 miles)"
        
        # Standard Consistent Cruiser advice
        rec["intensity_focus"] = "Add 1 quality workout: tempo run (20 min at comfortably hard pace)"
        rec["recovery_advice"] = "Active recovery on rest days: easy cycling, swimming, or yoga"
        rec["weekly_structure"] = """
        Suggested Week:
        • 3 easy runs (30-45 min each)
        • 1 tempo run or hill workout (30-40 min total)
        • 1 long run (60-90 min)
        • 2 rest or active recovery days
        """
        
        return rec
    
    def _competitive_peak_rules(self, rec, fatigue, mileage, mileage_change_pct, weeks_until_race):
        """Rules for Competitive Peak cluster (Cluster 2)."""
        
        # Critical fatigue check
        if fatigue > 45:
            rec["action"] = "mandatory_recovery"
            rec["volume_recommendation"] = "Cut mileage by 30-40% immediately"
            rec["caution_flags"].append("CRITICAL: Fatigue approaching overtraining - mandatory rest")
        
        # High fatigue warning
        elif fatigue > 35:
            rec["action"] = "reduce_volume"
            rec["volume_recommendation"] = "Reduce mileage by 15-20% this week"
            rec["caution_flags"].append("High fatigue - prioritize recovery to avoid injury")
        
        # Taper phase (if race approaching)
        elif weeks_until_race and weeks_until_race <= 2:
            rec["action"] = "taper"
            rec["volume_recommendation"] = "Reduce volume by 20-40% while maintaining intensity"
            rec["caution_flags"].append("Taper phase - prioritize freshness over fitness")
        
        # Peak training phase
        elif mileage >= 30:
            rec["action"] = "maintain_or_build"
            rec["volume_recommendation"] = "Maintain current volume or increase by max 5% (1-2 miles)"
        
        # Building to peak
        else:
            rec["action"] = "progressive_build"
            rec["volume_recommendation"] = "Increase mileage by 5-8% (1.5-2.5 miles)"
        
        # Standard Competitive Peak advice
        rec["intensity_focus"] = "2 quality sessions: 1 interval workout + 1 tempo run"
        rec["recovery_advice"] = """
        Critical recovery protocols:
        • 8+ hours sleep nightly
        • Post-run nutrition within 30 minutes
        • Weekly sports massage or foam rolling
        • Monitor morning heart rate for overtraining signs
        """
        rec["weekly_structure"] = """
        Suggested Week:
        • 2-3 easy runs (45-60 min each)
        • 1 interval session (track repeats or fartlek)
        • 1 tempo run (30-40 min at threshold pace)
        • 1 long run (90-120 min)
        • 1-2 rest or very easy recovery days
        """
        
        return rec
    
    def _apply_race_adjustments(self, rec, race_distance, weeks_until_race):
        """Apply race-specific adjustments to recommendation."""
        
        race_names = {
            3.1: "5K",
            6.2: "10K", 
            13.1: "Half Marathon",
            26.2: "Marathon"
        }
        
        race_name = race_names.get(race_distance, f"{race_distance} mile race")
        
        # Add race context
        rec["goal_race"] = race_name
        rec["weeks_until_race"] = weeks_until_race
        
        # Taper recommendations
        if weeks_until_race <= 2:
            rec["race_specific_advice"] = f"""
            TAPER PHASE for {race_name}:
            • Reduce volume by 20-40%
            • Maintain workout intensity but reduce duration
            • Prioritize rest and mental preparation
            • No new workouts or experiments
            • Focus on race logistics and nutrition plan
            """
        
        # Peak training phase
        elif weeks_until_race <= 8:
            rec["race_specific_advice"] = f"""
            PEAK TRAINING for {race_name}:
            • Include race-pace specific workouts
            • Practice race-day nutrition strategy
            • Simulate race conditions (time of day, terrain)
            • Build mental toughness with challenging sessions
            """
        
        # Base building phase
        else:
            rec["race_specific_advice"] = f"""
            BASE BUILDING for {race_name}:
            • Focus on aerobic base development
            • Gradually build weekly mileage
            • Limited intensity work (80/20 easy/hard split)
            • Establish consistent training routine
            """
        
        return rec


# Testing function
def test_recommender():
    """Test the recommender with sample data."""
    
    recommender = RunningRecommender()
    
    # Test Case 1: Foundation Builder with low training frequency
    print("="*80)
    print("TEST CASE 1: Foundation Builder - Low Training Frequency")
    print("="*80)
    rec1 = recommender.get_recommendation(
        cluster_id=0,
        current_weekly_mileage=10.0,
        predicted_next_week_mileage=11.5,
        current_fatigue_index=8.5,
        training_days_per_week=2
    )
    print(f"Action: {rec1['action']}")
    print(f"Volume: {rec1['volume_recommendation']}")
    print(f"Cautions: {rec1['caution_flags']}")
    
    # Test Case 2: Consistent Cruiser with high fatigue
    print("\n" + "="*80)
    print("TEST CASE 2: Consistent Cruiser - High Fatigue")
    print("="*80)
    rec2 = recommender.get_recommendation(
        cluster_id=1,
        current_weekly_mileage=22.0,
        predicted_next_week_mileage=25.0,
        current_fatigue_index=32.0,
        training_days_per_week=3
    )
    print(f"Action: {rec2['action']}")
    print(f"Volume: {rec2['volume_recommendation']}")
    print(f"Cautions: {rec2['caution_flags']}")
    
    # Test Case 3: Competitive Peak with race approaching
    print("\n" + "="*80)
    print("TEST CASE 3: Competitive Peak - Race in 2 Weeks")
    print("="*80)
    rec3 = recommender.get_recommendation(
        cluster_id=2,
        current_weekly_mileage=38.0,
        predicted_next_week_mileage=40.0,
        current_fatigue_index=36.0,
        training_days_per_week=4,
        goal_race_distance=13.1,
        weeks_until_race=2
    )
    print(f"Action: {rec3['action']}")
    print(f"Volume: {rec3['volume_recommendation']}")
    print(f"Race Advice: {rec3.get('race_specific_advice', 'N/A')[:100]}...")
    print(f"Cautions: {rec3['caution_flags']}")


if __name__ == "__main__":
    test_recommender()
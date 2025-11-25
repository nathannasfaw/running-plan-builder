"""
Comprehensive testing for RunningRecommender
Tests all cluster types and edge cases
"""

from recommender import RunningRecommender
import json


def print_recommendation(rec, title):
    """Pretty print a recommendation."""
    print("\n" + "="*80)
    print(title)
    print("="*80)
    print(f"Cluster: {rec['cluster_name']} (ID: {rec['cluster_id']})")
    print(f"Current Mileage: {rec['current_mileage']:.1f} miles")
    print(f"Predicted Mileage: {rec['predicted_mileage']:.1f} miles ({rec['mileage_change']:+.1f} miles, {rec['mileage_change_pct']:+.1f}%)")
    print(f"Fatigue Index: {rec['current_fatigue']:.1f}")
    print(f"Training Days: {rec['training_days']:.1f}")
    print(f"\nACTION: {rec['action']}")
    print(f"VOLUME: {rec['volume_recommendation']}")
    print(f"INTENSITY: {rec['intensity_focus']}")
    print(f"RECOVERY: {rec['recovery_advice'][:100]}...")
    
    if rec['caution_flags']:
        print(f"\n⚠️  CAUTIONS:")
        for flag in rec['caution_flags']:
            print(f"   • {flag}")
    
    if 'goal_race' in rec:
        print(f"\n🏁 RACE: {rec['goal_race']} in {rec['weeks_until_race']} weeks")
    
    print("\nWEEKLY STRUCTURE:")
    print(rec['weekly_structure'])


def test_foundation_builder():
    """Test Foundation Builder (Cluster 0) scenarios."""
    recommender = RunningRecommender()
    
    print("\n" + "#"*80)
    print("# TESTING FOUNDATION BUILDER (Cluster 0)")
    print("#"*80)
    
    # Scenario 1: Low training frequency
    rec1 = recommender.get_recommendation(
        cluster_id=0,
        current_weekly_mileage=10.0,
        predicted_next_week_mileage=11.0,
        current_fatigue_index=8.0,
        training_days_per_week=2
    )
    print_recommendation(rec1, "SCENARIO 1: Low Training Frequency")
    assert rec1['action'] == 'build_consistency'
    
    # Scenario 2: High fatigue
    rec2 = recommender.get_recommendation(
        cluster_id=0,
        current_weekly_mileage=12.0,
        predicted_next_week_mileage=13.0,
        current_fatigue_index=22.0,
        training_days_per_week=3
    )
    print_recommendation(rec2, "SCENARIO 2: High Fatigue for Beginner")
    assert rec2['action'] == 'recovery_focus'
    
    # Scenario 3: Excessive mileage increase
    rec3 = recommender.get_recommendation(
        cluster_id=0,
        current_weekly_mileage=10.0,
        predicted_next_week_mileage=12.0,
        current_fatigue_index=10.0,
        training_days_per_week=3
    )
    print_recommendation(rec3, "SCENARIO 3: Too Fast Progression (20% increase)")
    assert rec3['action'] == 'slow_progression'
    
    # Scenario 4: Normal progression
    rec4 = recommender.get_recommendation(
        cluster_id=0,
        current_weekly_mileage=10.0,
        predicted_next_week_mileage=10.8,
        current_fatigue_index=12.0,
        training_days_per_week=3
    )
    print_recommendation(rec4, "SCENARIO 4: Normal Progression (8% increase)")
    assert rec4['action'] == 'gradual_build'


def test_consistent_cruiser():
    """Test Consistent Cruiser (Cluster 1) scenarios."""
    recommender = RunningRecommender()
    
    print("\n" + "#"*80)
    print("# TESTING CONSISTENT CRUISER (Cluster 1)")
    print("#"*80)
    
    # Scenario 1: High fatigue
    rec1 = recommender.get_recommendation(
        cluster_id=1,
        current_weekly_mileage=22.0,
        predicted_next_week_mileage=25.0,
        current_fatigue_index=32.0,
        training_days_per_week=3
    )
    print_recommendation(rec1, "SCENARIO 1: High Fatigue")
    assert rec1['action'] == 'recovery_week'
    
    # Scenario 2: Stagnation (low mileage change)
    rec2 = recommender.get_recommendation(
        cluster_id=1,
        current_weekly_mileage=20.0,
        predicted_next_week_mileage=20.2,
        current_fatigue_index=22.0,
        training_days_per_week=3
    )
    print_recommendation(rec2, "SCENARIO 2: Stagnation (1% change)")
    assert rec2['action'] == 'progressive_overload'
    
    # Scenario 3: Excessive increase
    rec3 = recommender.get_recommendation(
        cluster_id=1,
        current_weekly_mileage=20.0,
        predicted_next_week_mileage=23.0,
        current_fatigue_index=24.0,
        training_days_per_week=3
    )
    print_recommendation(rec3, "SCENARIO 3: Too Fast Increase (15%)")
    assert rec3['action'] == 'moderate_increase'
    
    # Scenario 4: Normal progression
    rec4 = recommender.get_recommendation(
        cluster_id=1,
        current_weekly_mileage=20.0,
        predicted_next_week_mileage=22.0,
        current_fatigue_index=24.0,
        training_days_per_week=3
    )
    print_recommendation(rec4, "SCENARIO 4: Normal Progression (10%)")
    assert rec4['action'] == 'balanced_progression'


def test_competitive_peak():
    """Test Competitive Peak (Cluster 2) scenarios."""
    recommender = RunningRecommender()
    
    print("\n" + "#"*80)
    print("# TESTING COMPETITIVE PEAK (Cluster 2)")
    print("#"*80)
    
    # Scenario 1: Critical fatigue
    rec1 = recommender.get_recommendation(
        cluster_id=2,
        current_weekly_mileage=35.0,
        predicted_next_week_mileage=38.0,
        current_fatigue_index=48.0,
        training_days_per_week=4
    )
    print_recommendation(rec1, "SCENARIO 1: Critical Fatigue (48)")
    assert rec1['action'] == 'mandatory_recovery'
    
    # Scenario 2: High fatigue
    rec2 = recommender.get_recommendation(
        cluster_id=2,
        current_weekly_mileage=35.0,
        predicted_next_week_mileage=37.0,
        current_fatigue_index=38.0,
        training_days_per_week=4
    )
    print_recommendation(rec2, "SCENARIO 2: High Fatigue (38)")
    assert rec2['action'] == 'reduce_volume'
    
    # Scenario 3: Race taper (2 weeks out)
    rec3 = recommender.get_recommendation(
        cluster_id=2,
        current_weekly_mileage=35.0,
        predicted_next_week_mileage=38.0,
        current_fatigue_index=32.0,
        training_days_per_week=4,
        goal_race_distance=13.1,
        weeks_until_race=2
    )
    print_recommendation(rec3, "SCENARIO 3: Race Taper (Half Marathon in 2 weeks)")
    assert rec3['action'] == 'taper'  # Changed from 'reduce_volume'
    assert 'goal_race' in rec3


def test_race_adjustments():
    """Test race-specific adjustments."""
    recommender = RunningRecommender()
    
    print("\n" + "#"*80)
    print("# TESTING RACE-SPECIFIC ADJUSTMENTS")
    print("#"*80)
    
    # Test different race distances
    races = [
        (3.1, "5K"),
        (6.2, "10K"),
        (13.1, "Half Marathon"),
        (26.2, "Marathon")
    ]
    
    for distance, name in races:
        # Taper phase (1 week out)
        rec_taper = recommender.get_recommendation(
            cluster_id=1,
            current_weekly_mileage=20.0,
            predicted_next_week_mileage=22.0,
            current_fatigue_index=24.0,
            training_days_per_week=3,
            goal_race_distance=distance,
            weeks_until_race=1
        )
        print_recommendation(rec_taper, f"{name} - Taper Phase (1 week)")
        assert 'TAPER PHASE' in rec_taper['race_specific_advice']
        
        # Peak training (6 weeks out)
        rec_peak = recommender.get_recommendation(
            cluster_id=1,
            current_weekly_mileage=20.0,
            predicted_next_week_mileage=22.0,
            current_fatigue_index=24.0,
            training_days_per_week=3,
            goal_race_distance=distance,
            weeks_until_race=6
        )
        assert 'PEAK TRAINING' in rec_peak['race_specific_advice']
        
        # Base building (12 weeks out)
        rec_base = recommender.get_recommendation(
            cluster_id=1,
            current_weekly_mileage=20.0,
            predicted_next_week_mileage=22.0,
            current_fatigue_index=24.0,
            training_days_per_week=3,
            goal_race_distance=distance,
            weeks_until_race=12
        )
        assert 'BASE BUILDING' in rec_base['race_specific_advice']


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    recommender = RunningRecommender()
    
    print("\n" + "#"*80)
    print("# TESTING EDGE CASES")
    print("#"*80)
    
    # Zero mileage change
    rec1 = recommender.get_recommendation(
        cluster_id=1,
        current_weekly_mileage=20.0,
        predicted_next_week_mileage=20.0,
        current_fatigue_index=24.0,
        training_days_per_week=3
    )
    print_recommendation(rec1, "EDGE CASE 1: Zero Mileage Change")
    
    # Very low mileage
    rec2 = recommender.get_recommendation(
        cluster_id=0,
        current_weekly_mileage=5.0,
        predicted_next_week_mileage=5.5,
        current_fatigue_index=6.0,
        training_days_per_week=2
    )
    print_recommendation(rec2, "EDGE CASE 2: Very Low Mileage (5 miles)")
    
    # Very high mileage
    rec3 = recommender.get_recommendation(
        cluster_id=2,
        current_weekly_mileage=50.0,
        predicted_next_week_mileage=52.0,
        current_fatigue_index=40.0,
        training_days_per_week=5
    )
    print_recommendation(rec3, "EDGE CASE 3: Very High Mileage (50 miles)")


def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*80)
    print("RUNNING COMPREHENSIVE RECOMMENDER TESTS")
    print("="*80)
    
    try:
        test_foundation_builder()
        print("\n✅ Foundation Builder tests passed!")
        
        test_consistent_cruiser()
        print("\n✅ Consistent Cruiser tests passed!")
        
        test_competitive_peak()
        print("\n✅ Competitive Peak tests passed!")
        
        test_race_adjustments()
        print("\n✅ Race adjustment tests passed!")
        
        test_edge_cases()
        print("\n✅ Edge case tests passed!")
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    run_all_tests()
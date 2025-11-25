"""
Natural Language Generation Handler
Converts structured recommendations into friendly, human-readable training plans
using Gemini (Google AI Studio) API
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class LLMHandler:
    """
    Handles Natural Language Generation for training plan recommendations.
    Uses Gemini API to convert structured data into friendly, conversational text.
    """
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")
        genai.configure(api_key=api_key)
        # Use a supported model name for the Python SDK
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def get_friendly_plan(self, recommendation_dict):
        """
        Generate a friendly, human-readable training plan from structured recommendation.
        """
        prompt = self._build_prompt(recommendation_dict)
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating training plan: {str(e)}"

    def _build_prompt(self, rec):
        coach_instructions = (
            "You are an experienced running coach who creates personalized, encouraging training plans. "
            "Your tone is friendly, supportive, and motivating. "
            "You explain the reasoning behind recommendations and make runners feel confident about their training. "
            "Keep responses concise but comprehensive.\n"
        )
        cautions = ""
        if rec['caution_flags']:
            cautions = "\nIMPORTANT CAUTIONS:\n" + "\n".join(f"  • {flag}" for flag in rec['caution_flags'])
        race_info = ""
        if 'goal_race' in rec and 'weeks_until_race' in rec:
            race_info = f"\n🏁 GOAL RACE: {rec['goal_race']} in {rec['weeks_until_race']} weeks"
            if 'race_specific_advice' in rec:
                race_info += f"\n{rec['race_specific_advice']}"
        prompt = f"""{coach_instructions}
Create a personalized weekly running plan for this runner.

RUNNER PROFILE:
  • Level: {rec['cluster_name']}
  • Current Weekly Mileage: {rec['current_mileage']:.1f} miles
  • Predicted Next Week: {rec['predicted_mileage']:.1f} miles ({rec['mileage_change']:+.1f} miles, {rec['mileage_change_pct']:+.1f}%)
  • Current Fatigue Index: {rec['current_fatigue']:.1f}
  • Training Days per Week: {rec['training_days']:.1f}

RECOMMENDATION:
  • Action: {rec['action']}
  • Volume: {rec['volume_recommendation']}
  • Intensity Focus: {rec['intensity_focus']}
  • Recovery: {rec['recovery_advice']}
{cautions}
{race_info}

First, provide a summary of the types of workouts included this week (e.g., easy runs, long run, tempo, rest, cross-training).

Then, provide the weekly schedule as a Markdown table with columns: 'Day', 'Activity', 'Mileage (mi)', 'Time (min)', and 'Pace'. 
- For each day, fill in the appropriate columns (leave blank if not applicable).
- For easy runs, use "easy/conversational pace" for pace.
- For workouts, specify pace as "tempo pace", "interval pace", etc.
- For rest/cross-training, leave mileage/time/pace blank.

After the table, include a brief explanation and encouragement, but do NOT repeat the table or weekly schedule in prose.
"""
        return prompt
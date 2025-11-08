"""
Test script for GitHub Profile Analysis
"""
import requests
import json


def test_github_analysis(username: str = "tulika-anand"):
    """Test GitHub profile analysis endpoint"""
    print(f"\n🔍 Testing GitHub Analysis for: {username}")
    print("=" * 60)
    
    url = f"http://localhost:8000/analyze/github/{username}"
    
    try:
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ Analysis Successful!\n")
            
            # User Info
            user = result.get('user_info', {})
            print(f"👤 User: {user.get('name')} (@{user.get('username')})")
            print(f"📍 Location: {user.get('location', 'Not specified')}")
            print(f"🏢 Company: {user.get('company', 'Not specified')}")
            print(f"📝 Bio: {user.get('bio', 'No bio')}")
            print(f"👥 Followers: {user.get('followers')} | Following: {user.get('following')}")
            print(f"📦 Public Repos: {user.get('public_repos')}")
            
            # Stats
            stats = result.get('stats', {})
            print(f"\n📊 Statistics:")
            print(f"   Languages: {', '.join(stats.get('languages_used', {}).keys())}")
            print(f"   ⭐ Total Stars: {stats.get('total_stars_earned', 0)}")
            print(f"   🍴 Total Forks: {stats.get('total_forks', 0)}")
            
            # AI Analysis
            analysis = result.get('analysis', {})
            print(f"\n🤖 AI Analysis:")
            print(f"   Experience Level: {analysis.get('overall_experience_level', 'Unknown')}")
            print(f"   Estimated Years: {analysis.get('experience_years_estimate', 'Unknown')}")
            
            # Skills
            skills = analysis.get('skills_with_scores', {})
            if skills:
                print(f"\n💪 Top Skills (Scored 1-10):")
                sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
                for skill, score in sorted_skills[:10]:
                    print(f"   {skill}: {score}/10")
            
            # Domains
            tech_stack = analysis.get('dominant_tech_stack', {})
            domains = tech_stack.get('domains', [])
            if domains:
                print(f"\n🎯 Dominant Domains:")
                for domain in domains:
                    print(f"   • {domain}")
            
            # Notable Projects
            project_analysis = analysis.get('project_analysis', {})
            notable = project_analysis.get('notable_projects', [])
            if notable:
                print(f"\n🌟 Notable Projects:")
                for proj in notable[:5]:
                    print(f"   • {proj['name']}")
                    print(f"     Description: {proj['description']}")
                    print(f"     Complexity: {proj['complexity_score']}/10 | Impact: {proj['impact_score']}/10")
                    print(f"     Stars: {proj['stars']} | Tech: {', '.join(proj.get('technologies', []))}")
                    print()
            
            # Strengths
            strengths = analysis.get('strengths', [])
            if strengths:
                print(f"✅ Strengths:")
                for strength in strengths:
                    print(f"   • {strength}")
            
            # Areas for Growth
            growth = analysis.get('areas_for_growth', [])
            if growth:
                print(f"\n📈 Areas for Growth:")
                for area in growth:
                    print(f"   • {area}")
            
            # Summary
            summary = analysis.get('professional_summary', '')
            if summary:
                print(f"\n📄 Professional Summary:")
                print(f"   {summary}")
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")


def test_combined_analysis(github_username: str = "tulika-anand"):
    """Test combined resume + GitHub analysis"""
    print(f"\n🔍 Testing Combined Analysis")
    print("=" * 60)
    
    url = "http://localhost:8000/analyze/combined"
    
    # You'll need a sample resume file
    print("Note: You need to provide a resume file for this test")
    print(f"Example: Use the sample_resume.txt created by test_sample.py")


def main():
    """Run GitHub analysis tests"""
    print("=" * 60)
    print("🧪 GitHub Profile Analyzer - Test Suite")
    print("=" * 60)
    print("\nMake sure the server is running on http://localhost:8000")
    
    input("\nPress Enter to start tests...")
    
    # Test with different usernames
    test_usernames = [
        "tulika-anand",
        # Add more usernames to test
    ]
    
    for username in test_usernames:
        test_github_analysis(username)
        print("\n" + "=" * 60 + "\n")
    
    print("\n✅ Tests completed!")
    print("\nNext steps:")
    print("1. Visit http://localhost:8000/docs for interactive API docs")
    print("2. Try: GET /analyze/github/{username}")
    print("3. Try: POST /analyze/combined with resume + GitHub username")


if __name__ == "__main__":
    main()

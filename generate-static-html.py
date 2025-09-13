#!/usr/bin/env python3
"""
Generate static HTML for Prophet with embedded data
This script fetches data from the localhost API and generates static HTML
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Any

API_BASE = 'http://localhost:5195'

def fetch_data(endpoint: str) -> Dict[str, Any]:
    """Fetch data from API endpoint"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return {}

def format_currency(amount: float) -> str:
    """Format currency"""
    return f"${amount:,.0f}"

def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value:.1f}%"

def format_bet_display(recommendation: Dict[str, Any]) -> str:
    """Format bet display"""
    game_info = recommendation.get('gameInfo', 'Unknown Game')
    bet_type = recommendation.get('betType', 0)
    side = recommendation.get('side', 0)
    line = recommendation.get('line')
    odds = recommendation.get('oddsAtTimeOfBet')
    
    [away_team, home_team] = game_info.split(' @ ')
    
    if bet_type == 0:  # Moneyline
        team = home_team if side == 0 else away_team
        odds_str = f"({odds:+d})" if odds else ""
        return f"{team} to Win {odds_str}"
    elif bet_type == 1:  # Spread
        spread_team = home_team if side == 0 else away_team
        spread_line = f"{line:+.1f}" if line is not None else ""
        odds_str = f" ({odds:+d})" if odds else ""
        return f"{spread_team} {spread_line}{odds_str}"
    elif bet_type == 2:  # Total
        over_under = "Over" if side == 2 else "Under"
        total_line = f"{line:.1f}" if line is not None else ""
        odds_str = f" ({odds:+d})" if odds else ""
        return f"{over_under} {total_line} Points{odds_str}"
    else:
        return "Unknown Bet Type"

def format_sportsbook_name(sportsbook: str) -> str:
    """Format sportsbook name"""
    name_map = {
        'DraftKings': 'DraftKings',
        'FanDuel': 'FanDuel',
        'BetMGM': 'BetMGM',
        'BetRivers': 'BetRivers',
        'Bovada': 'Bovada',
        'MyBookie.ag': 'MyBookie',
        'BetOnline.ag': 'BetOnline',
        'LowVig.ag': 'LowVig',
        'BetUS': 'BetUS'
    }
    return name_map.get(sportsbook, sportsbook)

def get_sportsbook_class(sportsbook: str) -> str:
    """Get CSS class for sportsbook"""
    class_map = {
        'DraftKings': 'draftkings',
        'FanDuel': 'fanduel',
        'BetMGM': 'betmgm',
        'BetRivers': 'betrivers',
        'Bovada': 'bovada',
        'MyBookie.ag': 'mybookie',
        'BetOnline.ag': 'betonline',
        'LowVig.ag': 'lowvig',
        'BetUS': 'betus'
    }
    return class_map.get(sportsbook, '')

def format_game_time(utc_datetime_string: str) -> str:
    """Format game time"""
    try:
        date = datetime.fromisoformat(utc_datetime_string.replace('Z', '+00:00'))
        return date.strftime('%b %d, %I:%M %p')
    except:
        return utc_datetime_string

def generate_recommendations_html(recommendations: List[Dict[str, Any]]) -> str:
    """Generate HTML for recommendations"""
    if not recommendations:
        return '''
        <div class="no-recommendations">
            <h3>No recommendations available</h3>
            <p>Check back later for betting recommendations.</p>
        </div>
        '''
    
    html = ''
    
    for rec in recommendations:
        is_top_pick = rec.get('isTopPick', False)
        confidence = rec.get('confidence', 0)
        reasoning = rec.get('reasoning', 'No reasoning provided')
        game_info = rec.get('gameInfo', 'Unknown Game')
        bet_display = format_bet_display(rec)
        sportsbook = format_sportsbook_name(rec.get('sportsbook', 'Unknown'))
        game_time = format_game_time(rec.get('gameTime', ''))
        wager_amount = rec.get('recommendedWager', 0)
        odds_value = rec.get('oddsAtTimeOfBet', 0)
        expected_value = rec.get('expectedValue', 0)
        kelly_percentage = rec.get('kellyPercentage', 0)
        
        # Format values
        confidence_str = f"{confidence:.1f}%"
        expected_value_str = f"{expected_value:.3f}"
        kelly_str = f"{kelly_percentage:.1f}%"
        wager_str = format_currency(wager_amount)
        
        # Get sportsbook class
        sportsbook_class = get_sportsbook_class(sportsbook)
        
        # Game details
        game_details = f"{game_info} • {game_time}"
        
        top_pick_class = 'top-pick' if is_top_pick else ''
        top_pick_badge = '<div class="top-pick-badge">TOP PICK</div>' if is_top_pick else ''
        
        html += f'''
        <div class="recommendation-card {top_pick_class}">
            {top_pick_badge}
            <div class="card-header">
                <div class="bet-info">
                    <div class="bet-text">
                        <h3>{bet_display}<span class="sportsbook-badge {sportsbook_class}">{sportsbook}</span></h3>
                        <div class="bet-details">{game_details}</div>
                    </div>
                </div>
                <div class="card-badges">
                    <div class="outcome-badge pending">PENDING</div>
                </div>
            </div>
            <div class="card-body">
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-label">Expected Value</div>
                        <div class="metric-value expected-value">{expected_value_str}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Confidence</div>
                        <div class="metric-value confidence">{confidence_str}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Kelly Criterion</div>
                        <div class="metric-value kelly">{kelly_str}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">BET</div>
                        <div class="metric-value wager">{wager_str}</div>
                    </div>
                </div>
                <div class="reasoning">
                    <div class="reasoning-label">Reasoning:</div>
                    <div class="reasoning-text">{reasoning}</div>
                </div>
            </div>
        </div>
        '''
    
    return html

def generate_performance_html(performance: Dict[str, Any]) -> str:
    """Generate HTML for performance metrics"""
    if not performance:
        return ''
    
    total_bets = performance.get('totalBets', 0)
    total_wager = performance.get('totalWager', 0)
    realized_pl = performance.get('realizedPl', 0)
    win_rate = performance.get('winRate', 0)
    roi = performance.get('roi', 0)
    
    return f'''
    <div class="performance-card">
        <h3>Overall Performance</h3>
        <table class="summary-table">
            <tr>
                <td class="summary-label">Completed Bets:</td>
                <td class="summary-value">{total_bets}</td>
                <td class="summary-label">Total Wager:</td>
                <td class="summary-value">{format_currency(total_wager)}</td>
                <td class="summary-label">Realized P&L:</td>
                <td class="summary-value">{format_currency(realized_pl)}</td>
                <td class="summary-label">Win Rate:</td>
                <td class="summary-value">{format_percentage(win_rate)}</td>
            </tr>
        </table>
    </div>
    '''

def generate_static_html():
    """Generate the complete static HTML"""
    
    # Fetch data from API
    print("Fetching data from API...")
    
    # Get current week
    week_info = fetch_data('/api/nfl-week/current')
    current_week = week_info.get('currentWeek', 1)
    total_weeks = week_info.get('totalWeeks', 18)
    
    # Get recommendations for current week
    recommendations_response = fetch_data(f'/api/recommendations/week/{current_week}')
    recommendations = recommendations_response.get('recommendations', [])
    
    # Get performance data
    performance = fetch_data('/api/analytics/performance')
    
    # Get games for current week
    games = fetch_data(f'/api/games/week/{current_week}')
    
    print(f"Found {len(recommendations)} recommendations for week {current_week}")
    
    # Generate HTML for current week
    recommendations_html = generate_recommendations_html(recommendations)
    performance_html = generate_performance_html(performance)
    
    # Fetch data for all weeks for navigation
    all_weeks_data = {}
    for week_num in range(1, total_weeks + 1):
        print(f"Fetching data for week {week_num}...")
        
        week_info = fetch_data(f'/api/nfl-week/{week_num}')
        recommendations_response = fetch_data(f'/api/recommendations/week/{week_num}')
        recommendations = recommendations_response.get('recommendations', [])
        games = fetch_data(f'/api/games/week/{week_num}')
        
        all_weeks_data[week_num] = {
            'weekInfo': week_info,
            'recommendations': recommendations,
            'performance': performance,  # Use same performance data for all weeks
            'games': games
        }
        
        print(f"Found {len(recommendations)} recommendations for week {week_num}")
    
    # Format week dates
    week_start = week_info.get('weekStartDate', '')
    week_end = week_info.get('weekEndDate', '')
    week_dates = f"Week {current_week}"
    if week_start and week_end:
        try:
            # Handle timezone properly - remove the timezone part first
            start_clean = week_start.split('+')[0].split('Z')[0]
            end_clean = week_end.split('+')[0].split('Z')[0]
            
            start_date = datetime.fromisoformat(start_clean)
            end_date = datetime.fromisoformat(end_clean)
            
            # Format dates properly
            if start_date.month == end_date.month:
                week_dates = f"{start_date.strftime('%b %d')}-{end_date.strftime('%d')}, {start_date.year}"
            else:
                week_dates = f"{start_date.strftime('%b %d')}-{end_date.strftime('%b %d')}, {start_date.year}"
        except Exception as e:
            print(f"Error parsing dates: {e}")
            print(f"Start: {week_start}, End: {week_end}")
            week_dates = f"Week {current_week}"
    
    # Determine if next week button should be shown
    next_week_button = '<button class="week-nav-btn" id="nextWeekBtn" onclick="changeWeek(1)">›</button>' if current_week < total_weeks else ''
    
    # Generate the complete HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prophet - AI-Powered NFL Betting Recommendations</title>
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="shortcut icon" href="favicon.ico">
    
    <!-- CSS Files -->
    <link rel="stylesheet" href="css/main.css">
    <link rel="stylesheet" href="css/components.css">
    <link rel="stylesheet" href="css/performance.css">
    <link rel="stylesheet" href="css/responsive.css">
</head>
<body>
    <div class="container">
        <div class="top-header">
            <div class="week-info">
                <div class="week-navigation">
                    <button class="week-nav-btn" id="prevWeekBtn" onclick="changeWeek(-1)">‹</button>
                    <div class="week-display">
                        <h3 id="weekTitle">Week {current_week} of {total_weeks}</h3>
                        <div id="weekDates">{week_dates}</div>
                    </div>
                    {next_week_button}
                </div>
            </div>
            <div class="bankroll-info">
                <h3>Remaining Bankroll</h3>
                <div class="bankroll-amount-container">
                    <div class="bankroll-amount" id="header-bankroll">$10,000</div>
                    <div class="bankroll-roi" id="header-roi">0.0%</div>
                </div>
                <div class="bankroll-performance" id="header-performance">0% (0-0)</div>
            </div>
        </div>

        <div class="header">
            <div class="logo-container">
                <div class="logo-main">Prophet</div>
            </div>
            <p>AI-Powered Football Betting Recommendations</p>
        </div>

        <div class="recommendations">
            <!-- Performance Metrics Section -->
            <div id="performance-container" style="display: block;">
                <div class="performance-card">
                    <h3>Overall Performance</h3>
                    <table class="summary-table">
                        <tr>
                            <td class="summary-label">Completed Bets:</td>
                            <td class="summary-value" id="total-bets">0</td>
                            <td class="summary-label">Total Wager:</td>
                            <td class="summary-value" id="overall-total-wager">$0</td>
                            <td class="summary-label">Realized P&L:</td>
                            <td class="summary-value" id="total-pl">$0</td>
                            <td class="summary-label">Win Rate:</td>
                            <td class="summary-value" id="win-rate">0%</td>
                        </tr>
                        <tr class="top-picks-row">
                            <td class="top-picks-badge-cell"><div class="top-picks-badge-small indented">TOP PICKS</div></td>                                                                                           
                            <td class="summary-value" id="overall-top-picks-count">0</td>
                            <td class="summary-label">Wager:</td>
                            <td class="summary-value" id="overall-top-picks-wager">$0</td>
                            <td class="summary-label">Realized P&L:</td>
                            <td class="summary-value" id="overall-top-picks-pl">$0</td>
                            <td class="summary-label">Win Rate:</td>
                            <td class="summary-value" id="overall-top-picks-win-rate">0%</td>
                        </tr>
                        <tr class="other-bets-row">
                            <td class="other-bets-badge-cell"><div class="other-bets-badge-small indented">OTHER BETS</div></td>                                                                                        
                            <td class="summary-value" id="overall-other-bets-count">0</td>
                            <td class="summary-label">Wager:</td>
                            <td class="summary-value" id="overall-other-bets-wager">$0</td>
                            <td class="summary-label">Realized P&L:</td>
                            <td class="summary-value" id="overall-other-bets-pl">$0</td>
                            <td class="summary-label">Win Rate:</td>
                            <td class="summary-value" id="overall-other-bets-win-rate">0%</td>
                        </tr>
                    </table>
                </div>
            </div>

            <!-- Weekly Summary Section -->
            <div id="weekly-container" style="display: block;">
                <div class="summary-card">
                    <h3 id="weekly-summary-title">Week {current_week} Summary</h3>
                    <table class="summary-table">
                        <tr>
                            <td class="summary-label">Total Bets:</td>
                            <td class="summary-value" id="number-of-bets">{len(recommendations)}</td>
                            <td class="summary-label">Total Wager:</td>
                            <td class="summary-value" id="total-wager">$0</td>
                            <td class="summary-label">Realized P&L:</td>
                            <td class="summary-value" id="realized-pl">$0 (0%)</td>
                            <td class="summary-label">At Risk:</td>
                            <td class="summary-value" id="at-risk">$0</td>
                        </tr>
                        <tr class="top-picks-row">
                            <td class="top-picks-badge-cell">
                                <div class="top-picks-badge-small indented">TOP PICKS</div>
                            </td>
                            <td class="summary-value" id="top-picks-count">0</td>
                            <td class="summary-label">Wager:</td>
                            <td class="summary-value" id="top-picks-wager">$0</td>
                            <td class="summary-label">Realized P&L:</td>
                            <td class="summary-value" id="top-picks-win-loss">$0 (0%)</td>
                            <td class="summary-label">At Risk:</td>
                            <td class="summary-value" id="top-picks-at-risk">$0</td>
                        </tr>
                        <tr class="other-bets-row">
                            <td class="other-bets-badge-cell">
                                <div class="other-bets-badge-small indented">OTHER BETS</div>
                            </td>
                            <td class="summary-value" id="other-bets-count">0</td>
                            <td class="summary-label">Wager:</td>
                            <td class="summary-value" id="other-bets-wager">$0</td>
                            <td class="summary-label">Realized P&L:</td>
                            <td class="summary-value" id="other-bets-win-loss">$0 (0%)</td>
                            <td class="summary-label">At Risk:</td>
                            <td class="summary-value" id="other-bets-at-risk">$0</td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div id="recommendations-container">
                {recommendations_html}
            </div>
        </div>
    </div>

    <!-- JavaScript Files -->
    <script src="js/utils.js?v=2"></script>
    <script src="js/navigation.js?v=2"></script>
    <script src="js/performance.js?v=2"></script>
    
    <!-- Static Data -->
    <script>
        // Static data for all weeks
        const staticData = {{
            currentWeek: {current_week},
            totalWeeks: {total_weeks},
            weeks: {json.dumps(all_weeks_data)}
        }};
        
        // Override API calls to use static data
        window.fetch = function(url) {{
            if (url.includes('/api/nfl-week/')) {{
                const week = url.match(/\\/(\\d+)$/)?.[1] || staticData.currentWeek;
                return Promise.resolve({{
                    json: () => Promise.resolve(staticData.weeks[week]?.weekInfo || {{}})
                }});
            }}
            if (url.includes('/api/recommendations/week/')) {{
                const week = url.match(/\\/(\\d+)$/)?.[1] || staticData.currentWeek;
                return Promise.resolve({{
                    json: () => Promise.resolve(staticData.weeks[week]?.recommendations || [])
                }});
            }}
            if (url.includes('/api/analytics/performance')) {{
                return Promise.resolve({{
                    json: () => Promise.resolve(staticData.weeks[staticData.currentWeek]?.performance || {{}})
                }});
            }}
            if (url.includes('/api/games/week/')) {{
                const week = url.match(/\\/(\\d+)$/)?.[1] || staticData.currentWeek;
                return Promise.resolve({{
                    json: () => Promise.resolve(staticData.weeks[week]?.games || [])
                }});
            }}
            return Promise.reject(new Error('API not available in static mode'));
        }};
        
        // Current week tracking - use existing variable from utils.js
        currentWeek = staticData.currentWeek;
        
        // Override displayRecommendations to work with static data
        window.displayRecommendations = function(recommendations) {{
            const container = document.getElementById('recommendations-container');
            if (!container) return;
            
            if (!recommendations || recommendations.length === 0) {{
                container.innerHTML = `
                    <div class="no-recommendations">
                        <h3>No recommendations available</h3>
                        <p>Check back later for betting recommendations.</p>
                    </div>
                `;
                return;
            }}
            
            // Generate recommendations HTML (simplified version)
            let html = '';
            recommendations.forEach(rec => {{
                const isTopPick = rec.isTopPick || false;
                const confidence = rec.confidence || 0;
                const reasoning = rec.reasoning || 'No reasoning provided';
                const gameInfo = rec.gameInfo || 'Unknown Game';
                const betDisplay = formatBetDisplay(rec);
                const sportsbook = rec.sportsbook || 'Unknown';
                const gameTime = formatGameTime(rec.gameTime || '');
                const wagerAmount = rec.recommendedWager || 0;
                const oddsValue = rec.oddsAtTimeOfBet || 0;
                const expectedValue = rec.expectedValue || 0;
                const kellyPercentage = rec.kellyPercentage || 0;
                const wasCorrect = rec.wasCorrect;
                const profitLoss = rec.profitLoss || 0;
                
                // Determine outcome status
                let outcomeStatus = 'PENDING';
                let outcomeClass = 'pending';
                if (wasCorrect !== null) {{
                    if (wasCorrect) {{
                        outcomeStatus = 'WIN';
                        outcomeClass = 'win';
                    }} else {{
                        outcomeStatus = 'LOSS';
                        outcomeClass = 'loss';
                    }}
                }}
                
                const confidenceStr = `${{(confidence * 100).toFixed(1)}}%`;
                const expectedValueStr = `${{expectedValue.toFixed(3)}}`;
                const kellyStr = `${{(kellyPercentage * 100).toFixed(1)}}%`;
                const wagerStr = formatCurrency(wagerAmount);
                const sportsbookClass = getSportsbookClass(sportsbook);
                const gameDetails = `${{gameInfo}} • ${{gameTime}}`;
                const topPickClass = isTopPick ? 'top-pick' : '';
                const topPickBadge = isTopPick ? '<div class="top-pick-badge">TOP PICK</div>' : '';
                
                html += `
                    <div class="recommendation-card ${{topPickClass}}">
                        ${{topPickBadge}}
                        <div class="card-header">
                            <div class="bet-info">
                                <div class="bet-text">
                                    <h3>${{betDisplay}}<span class="sportsbook-badge ${{sportsbookClass}}">${{sportsbook}}</span></h3>
                                    <div class="bet-details">${{gameDetails}}</div>
                                </div>
                            </div>
                            <div class="card-badges">
                                <div class="outcome-badge ${{outcomeClass}}">${{outcomeStatus}}</div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="metrics-grid">
                                <div class="metric">
                                    <div class="metric-label">Expected Value</div>
                                    <div class="metric-value expected-value">${{expectedValueStr}}</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">Confidence</div>
                                    <div class="metric-value confidence">${{confidenceStr}}</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">Kelly Criterion</div>
                                    <div class="metric-value kelly">${{kellyStr}}</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">BET</div>
                                    <div class="metric-value wager">${{wagerStr}}</div>
                                </div>
                            </div>
                            <div class="reasoning">
                                <div class="reasoning-label">Reasoning:</div>
                                <div class="reasoning-text">${{reasoning}}</div>
                            </div>
                        </div>
                    </div>
                `;
            }});
            
            container.innerHTML = html;
        }};
        
        // Override updateWeekNavigation to work with static data
        window.updateWeekNavigation = function() {{
            const weekTitle = document.getElementById('weekTitle');
            const weekDates = document.getElementById('weekDates');
            const prevBtn = document.getElementById('prevWeekBtn');
            const nextBtn = document.getElementById('nextWeekBtn');
            
            if (weekTitle) {{
                weekTitle.textContent = `Week ${{currentWeek}} of ${{staticData.totalWeeks}}`;
            }}
            
            if (weekDates && staticData.weeks[currentWeek]) {{
                const weekInfo = staticData.weeks[currentWeek].weekInfo;
                const startDate = new Date(weekInfo.weekStartDate);
                const endDate = new Date(weekInfo.weekEndDate);
                const startStr = startDate.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric' }});
                const endStr = endDate.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric' }});
                weekDates.textContent = `${{startStr}} - ${{endStr}}`;
            }}
            
            if (prevBtn) {{
                const hasPrevWeek = currentWeek > 1 && staticData.weeks[currentWeek - 1] && staticData.weeks[currentWeek - 1].recommendations && staticData.weeks[currentWeek - 1].recommendations.length > 0;
                prevBtn.style.display = hasPrevWeek ? 'block' : 'none';
                prevBtn.disabled = !hasPrevWeek;
            }}
            
            if (nextBtn) {{
                const hasNextWeek = currentWeek < staticData.totalWeeks && staticData.weeks[currentWeek + 1] && staticData.weeks[currentWeek + 1].recommendations && staticData.weeks[currentWeek + 1].recommendations.length > 0;
                nextBtn.style.display = hasNextWeek ? 'block' : 'none';
                nextBtn.disabled = !hasNextWeek;
            }}
        }};
        
        // Override updateWeekDates to work with static data
        window.updateWeekDates = function() {{
            // This is handled by updateWeekNavigation
        }};
        
        // Override changeWeek to work with static data
        window.changeWeek = function(direction) {{
            const newWeek = currentWeek + direction;
            if (newWeek < 1 || newWeek > staticData.totalWeeks) return;
            
            currentWeek = newWeek;
            
            // Update week display
            updateWeekNavigation();
            
            // Load week data
            const weekData = staticData.weeks[currentWeek];
            if (weekData) {{
                displayRecommendations(weekData.recommendations);
                updatePerformanceDisplay(weekData.performance);
                updateWeeklySummary(weekData);
            }}
        }};
        
        // Helper functions for formatting
        function formatCurrency(amount) {{
            return `$${{Math.round(amount)}}`;
        }}
        
        function formatGameTime(timeStr) {{
            if (!timeStr) return '';
            const date = new Date(timeStr);
            return date.toLocaleDateString('en-US', {{ 
                weekday: 'short', 
                month: 'short', 
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            }});
        }}
        
        function formatBetDisplay(rec) {{
            const gameInfo = rec.gameInfo || 'Unknown Game';
            const betType = rec.betType; // 0=Moneyline, 1=Spread, 2=Total
            const side = rec.side;
            const line = rec.line;
            const odds = rec.oddsAtTimeOfBet;
            
            // Parse team names from gameInfo
            const [awayTeam, homeTeam] = gameInfo.split(' @ ');
            
            if (betType === 0) {{
                // Moneyline
                const team = side === 0 ? homeTeam : awayTeam;
                const oddsStr = odds ? ` (${{odds > 0 ? '+' : ''}}${{odds}})` : '';
                return `${{team}} to Win${{oddsStr}}`;
            }} else if (betType === 1) {{
                // Spread
                const team = side === 0 ? homeTeam : awayTeam;
                const lineStr = line ? `${{line > 0 ? '+' : ''}}${{line}}` : '';
                const oddsStr = odds ? ` (${{odds > 0 ? '+' : ''}}${{odds}})` : '';
                return `${{team}} ${{lineStr}}${{oddsStr}}`;
            }} else if (betType === 2) {{
                // Total
                const overUnder = side === 2 ? 'Over' : 'Under';
                const totalLine = line ? `${{line}}` : '';
                const oddsStr = odds ? ` (${{odds > 0 ? '+' : ''}}${{odds}})` : '';
                return `${{overUnder}} ${{totalLine}} Points${{oddsStr}}`;
            }}
            return 'Unknown Bet';
        }}
        
        function getSportsbookClass(sportsbook) {{
            const classes = {{
                'DraftKings': 'draftkings',
                'FanDuel': 'fanduel',
                'BetMGM': 'betmgm',
                'Caesars': 'caesars',
                'BetRivers': 'betrivers',
                'BetOnline.ag': 'betonline',
                'LowVig.ag': 'lowvig',
                'Bovada': 'bovada'
            }};
            return classes[sportsbook] || 'default';
        }}
        
        function updatePerformanceDisplay(performance) {{
            if (!performance) return;
            
            // Update overall performance metrics
            document.getElementById('total-bets').textContent = performance.totalBets || 0;
            document.getElementById('overall-total-wager').textContent = formatCurrency(performance.totalWager || 0);
            
            const totalPl = performance.totalProfitLoss || 0;
            const totalPlElement = document.getElementById('total-pl');
            totalPlElement.textContent = formatCurrency(totalPl);
            totalPlElement.className = totalPl >= 0 ? 'summary-value positive' : 'summary-value negative';
            
            document.getElementById('win-rate').textContent = formatPercentage(performance.winRate || 0);
            
            // Update top picks metrics
            document.getElementById('overall-top-picks-count').textContent = performance.topPicksCount || 0;
            document.getElementById('overall-top-picks-wager').textContent = formatCurrency(performance.topPicksWager || 0);
            
            const topPicksPl = performance.topPicksProfitLoss || 0;
            const topPicksPlElement = document.getElementById('overall-top-picks-pl');
            topPicksPlElement.textContent = formatCurrency(topPicksPl);
            topPicksPlElement.className = topPicksPl >= 0 ? 'summary-value positive' : 'summary-value negative';
            
            document.getElementById('overall-top-picks-win-rate').textContent = formatPercentage(performance.topPicksWinRate || 0);
            
            // Update other bets metrics
            const otherBetsCount = (performance.totalBets || 0) - (performance.topPicksCount || 0);
            const otherBetsWager = (performance.totalWager || 0) - (performance.topPicksWager || 0);
            const otherBetsPl = (performance.totalProfitLoss || 0) - (performance.topPicksProfitLoss || 0);
            const otherBetsWinRate = otherBetsCount > 0 ? (performance.winRate || 0) : 0; // Simplified
            
            document.getElementById('overall-other-bets-count').textContent = otherBetsCount;
            document.getElementById('overall-other-bets-wager').textContent = formatCurrency(otherBetsWager);
            
            const otherBetsPlElement = document.getElementById('overall-other-bets-pl');
            otherBetsPlElement.textContent = formatCurrency(otherBetsPl);
            otherBetsPlElement.className = otherBetsPl >= 0 ? 'summary-value positive' : 'summary-value negative';
            
            document.getElementById('overall-other-bets-win-rate').textContent = formatPercentage(otherBetsWinRate);
            
            // Update bankroll
            const remainingBankroll = 10000 + (performance.totalProfitLoss || 0);
            const roi = (performance.totalProfitLoss || 0) / 10000;
            document.getElementById('header-bankroll').textContent = formatCurrency(remainingBankroll);
            document.getElementById('header-roi').textContent = formatPercentage(roi);
            document.getElementById('header-performance').textContent = `${{formatPercentage(performance.winRate || 0)}} (${{performance.totalBets || 0}}-0)`;
        }}
        
        function updateWeeklySummary(weekData) {{
            if (!weekData || !weekData.recommendations) return;
            
            const recommendations = weekData.recommendations;
            const totalBets = recommendations.length;
            const totalWager = recommendations.reduce((sum, rec) => sum + (rec.recommendedWager || 0), 0);
            const totalPl = recommendations.reduce((sum, rec) => sum + (rec.profitLoss || 0), 0);
            const winCount = recommendations.filter(rec => rec.wasCorrect === true).length;
            const winRate = totalBets > 0 ? winCount / totalBets : 0;
            const atRisk = recommendations.filter(rec => rec.wasCorrect === null).reduce((sum, rec) => sum + (rec.recommendedWager || 0), 0);
            
            const topPicks = recommendations.filter(rec => rec.isTopPick);
            const topPicksCount = topPicks.length;
            const topPicksWager = topPicks.reduce((sum, rec) => sum + (rec.recommendedWager || 0), 0);
            const topPicksPl = topPicks.reduce((sum, rec) => sum + (rec.profitLoss || 0), 0);
            const topPicksWinCount = topPicks.filter(rec => rec.wasCorrect === true).length;
            const topPicksWinRate = topPicksCount > 0 ? topPicksWinCount / topPicksCount : 0;
            const topPicksAtRisk = topPicks.filter(rec => rec.wasCorrect === null).reduce((sum, rec) => sum + (rec.recommendedWager || 0), 0);
            
            const otherBets = recommendations.filter(rec => !rec.isTopPick);
            const otherBetsCount = otherBets.length;
            const otherBetsWager = otherBets.reduce((sum, rec) => sum + (rec.recommendedWager || 0), 0);
            const otherBetsPl = otherBets.reduce((sum, rec) => sum + (rec.profitLoss || 0), 0);
            const otherBetsWinCount = otherBets.filter(rec => rec.wasCorrect === true).length;
            const otherBetsWinRate = otherBetsCount > 0 ? otherBetsWinCount / otherBetsCount : 0;
            const otherBetsAtRisk = otherBets.filter(rec => rec.wasCorrect === null).reduce((sum, rec) => sum + (rec.recommendedWager || 0), 0);
            
            // Update weekly summary
            document.getElementById('number-of-bets').textContent = totalBets;
            document.getElementById('total-wager').textContent = formatCurrency(totalWager);
            
            const realizedPlElement = document.getElementById('realized-pl');
            realizedPlElement.textContent = `${{formatCurrency(totalPl)}} (${{formatPercentage(winRate)}})`;
            realizedPlElement.className = totalPl >= 0 ? 'summary-value positive' : 'summary-value negative';
            
            document.getElementById('at-risk').textContent = formatCurrency(atRisk);
            
            document.getElementById('top-picks-count').textContent = topPicksCount;
            document.getElementById('top-picks-wager').textContent = formatCurrency(topPicksWager);
            
            const topPicksWinLossElement = document.getElementById('top-picks-win-loss');
            topPicksWinLossElement.textContent = `${{formatCurrency(topPicksPl)}} (${{formatPercentage(topPicksWinRate)}})`;
            topPicksWinLossElement.className = topPicksPl >= 0 ? 'summary-value positive' : 'summary-value negative';
            
            document.getElementById('top-picks-at-risk').textContent = formatCurrency(topPicksAtRisk);
            
            document.getElementById('other-bets-count').textContent = otherBetsCount;
            document.getElementById('other-bets-wager').textContent = formatCurrency(otherBetsWager);
            
            const otherBetsWinLossElement = document.getElementById('other-bets-win-loss');
            otherBetsWinLossElement.textContent = `${{formatCurrency(otherBetsPl)}} (${{formatPercentage(otherBetsWinRate)}})`;
            otherBetsWinLossElement.className = otherBetsPl >= 0 ? 'summary-value positive' : 'summary-value negative';
            
            document.getElementById('other-bets-at-risk').textContent = formatCurrency(otherBetsAtRisk);
        }}
        
        function formatPercentage(value) {{
            return `${{Math.round(value * 100)}}%`;
        }}
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', () => {{
            // Initialize with static data
            updateWeekNavigation();
            displayRecommendations(staticData.weeks[currentWeek].recommendations);
            updatePerformanceDisplay(staticData.weeks[currentWeek].performance);
            updateWeeklySummary(staticData.weeks[currentWeek]);
        }});
    </script>
</body>
</html>'''
    
    return html

def main():
    """Main function"""
    print("Generating static HTML for Prophet...")
    
    # Generate HTML
    html_content = generate_static_html()
    
    # Write to file
    output_file = '/Users/kevin.bowling/Projects/prophet-public/index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Static HTML generated: {output_file}")
    
    # Copy CSS files
    css_files = ['main.css', 'components.css', 'performance.css', 'responsive.css']
    for css_file in css_files:
        src = f'/Users/kevin.bowling/Projects/prophet/Prophet.App/wwwroot/css/{css_file}'
        dst = f'/Users/kevin.bowling/Projects/prophet-public/css/{css_file}'
        
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, 'r') as f:
                content = f.read()
            with open(dst, 'w') as f:
                f.write(content)
            print(f"Copied {css_file}")
    
    # Copy JavaScript files
    js_files = ['utils.js', 'navigation.js', 'performance.js']
    for js_file in js_files:
        src = f'/Users/kevin.bowling/Projects/prophet/Prophet.App/wwwroot/js/{js_file}'
        dst = f'/Users/kevin.bowling/Projects/prophet-public/js/{js_file}'
        
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, 'r') as f:
                content = f.read()
            with open(dst, 'w') as f:
                f.write(content)
            print(f"Copied {js_file}")
    
    # Copy favicon
    favicon_src = '/Users/kevin.bowling/Projects/prophet/Prophet.App/wwwroot/favicon.ico'
    favicon_dst = '/Users/kevin.bowling/Projects/prophet-public/favicon.ico'
    if os.path.exists(favicon_src):
        with open(favicon_src, 'rb') as f:
            content = f.read()
        with open(favicon_dst, 'wb') as f:
            f.write(content)
        print("Copied favicon.ico")
    
    print("Static site generation complete!")

if __name__ == "__main__":
    main()

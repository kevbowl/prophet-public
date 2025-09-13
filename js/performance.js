// Performance metrics and summary functionality

// Load recommendations for current week
async function loadRecommendations() {
    try {
        const currentWeek = getCurrentWeek();
        const response = await fetch(`${API_BASE}/api/recommendations/week/${currentWeek}`);
        const data = await response.json();
        
        const recommendations = data.recommendations || [];
        const topPickIds = new Set(recommendations.filter(rec => rec.isTopPick).map(rec => rec.id));
        
        // Update available weeks based on recommendations
        if (recommendations && recommendations.length > 0) {
            availableWeeks.add(currentWeek);
        }
        
        // Display recommendations
        displayRecommendations(recommendations);
        
        // Update summary with current recommendations
        await updateSummary(recommendations, topPickIds);
        
        // Update navigation
        await updateWeekNavigation();
        
    } catch (error) {
        console.error('Error loading recommendations:', error);
        document.getElementById('recommendations-container').innerHTML = `
            <div class="error">
                <h3>Error loading recommendations</h3>
                <p>Please try refreshing the page.</p>
            </div>
        `;
    }
}

// Display recommendations in the UI
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = `
            <div class="no-recommendations">
                <h3>No recommendations available</h3>
                <p>No betting recommendations found for this week.</p>
            </div>
        `;
        return;
    }
    
    // Separate top picks and other bets
    const topPicks = recommendations.filter(rec => rec.isTopPick);
    const otherBets = recommendations.filter(rec => !rec.isTopPick);
    
    let html = '';
    
    // Top Picks section
    if (topPicks.length > 0) {
        html += '<div class="recommendations-section">';
        html += '<h3 class="section-title">TOP PICKS</h3>';
        html += '<div class="recommendations-grid">';
        topPicks.forEach((rec, index) => {
            html += createRecommendationCard(rec, index, true);
        });
        html += '</div></div>';
    }
    
    // Other Bets section
    if (otherBets.length > 0) {
        html += '<div class="recommendations-section">';
        html += '<h3 class="section-title">OTHER BETS</h3>';
        html += '<div class="recommendations-grid">';
        otherBets.forEach((rec, index) => {
            html += createRecommendationCard(rec, index, false);
        });
        html += '</div></div>';
    }
    
    container.innerHTML = html;
}

// Create recommendation card HTML
function createRecommendationCard(recommendation, index, isTopPick = false) {
    const betDisplay = formatBetDisplay(recommendation);
    const expectedValue = formatPercentage(recommendation.expectedValue);
    const confidence = formatPercentage(recommendation.confidence);
    const kelly = formatPercentage(recommendation.kellyPercentage);
    const wager = formatCurrency(recommendation.recommendedWager);
    const sportsbook = recommendation.sportsbook ? formatSportsbookName(recommendation.sportsbook) : '';
    const sportsbookClass = recommendation.sportsbook ? getSportsbookClass(recommendation.sportsbook) : '';
    
    // Format game time and channel info
    const gameTime = recommendation.gameTime ? formatGameTime(recommendation.gameTime) : '';
    const channelInfo = recommendation.tvNetwork ? formatChannelInfo(recommendation.tvNetwork, recommendation.broadcastType) : '';
    
    // Format game info with scores for completed games
    let gameInfo = recommendation.gameInfo || 'Unknown Game';
    if (recommendation.wasCorrect !== null && recommendation.homeScore !== null && recommendation.awayScore !== null) {
        // For completed games, show "FINAL: Away Team Score @ Home Team Score"
        const [awayTeam, homeTeam] = gameInfo.split(' @ ');
        gameInfo = `FINAL: ${awayTeam} ${recommendation.awayScore} @ ${homeTeam} ${recommendation.homeScore}`;
    }
    
    const gameDetails = [gameInfo, gameTime, channelInfo].filter(Boolean).join(' • ');

    return `
        <div class="recommendation-card ${isTopPick ? 'top-pick' : ''}">
            ${isTopPick ? '<div class="top-pick-badge">TOP PICK</div>' : ''}
            <div class="card-header">
                <div class="bet-info">
                    <div class="bet-text">
                        <h3>${betDisplay}${sportsbook ? `<span class="sportsbook-badge ${sportsbookClass}">${sportsbook}</span>` : ''}</h3>
                        <div class="bet-details">${gameDetails}</div>
                    </div>
                </div>
                <div class="card-badges">
                    ${recommendation.wasCorrect !== null ? 
                        `<div class="outcome-badge ${recommendation.wasCorrect ? 'win' : 'loss'}">${recommendation.wasCorrect ? 'WIN' : 'LOSS'}</div>` :
                        `<div class="outcome-badge pending">PENDING</div>`
                    }
                </div>
            </div>
            <div class="card-body">
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-label">Expected Value</div>
                        <div class="metric-value expected-value">${expectedValue}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Confidence</div>
                        <div class="metric-value confidence">${confidence}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Kelly Criterion</div>
                        <div class="metric-value kelly">${kelly}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">BET</div>
                        <div class="metric-value wager">
                            ${recommendation.wasCorrect !== null ? 
                                (recommendation.wasCorrect ? 
                                    `${wager} <span class="roi-inline profit">+${formatCurrency(recommendation.profitLoss)}</span>` :
                                    `<span class="loss">-${wager}</span>`
                                ) : 
                                wager
                            }
                        </div>
                    </div>
                </div>
                ${recommendation.reasoning ? `
                    <div class="reasoning">
                        <h4>Analysis ${recommendation.isFromGemini ? '<img src="/img/gemini-logo.png" alt="Gemini" style="height: 1em; vertical-align: middle; margin-left: 8px;">' : ''}</h4>
                        <p>${recommendation.reasoning}</p>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Centralized performance calculations

function calculateROI(profitLoss, wager) {
    // Calculate ROI as percentage: (profitLoss / wager) * 100
    if (wager === 0) return 0;
    return (profitLoss / wager) * 100;
}

function formatROI(profitLoss, wager) {
    // Calculate and format ROI consistently
    if (wager === 0) {
        return ''; // No percentage when wager is $0
    }
    const roi = calculateROI(profitLoss, wager);
    return `${Math.round(roi)}%`;
}

function calculateWinRate(wins, totalBets) {
    // Calculate win rate as decimal (0.0 to 1.0)
    if (totalBets === 0) return 0;
    return wins / totalBets;
}

function formatWinRate(wins, totalBets) {
    // Calculate and format win rate as percentage
    const winRate = calculateWinRate(wins, totalBets);
    return formatPercentage(winRate);
}

function getWlRecordColorClass(wins, losses) {
    // Return color class based on W/L ratio
    if (wins > losses) return 'positive';
    if (wins < losses) return 'negative';
    return ''; // Even record - no color class (white)
}

function formatWlRecord(wins, losses, asterisk = '') {
    // Format W/L record with consistent styling and color coding
    const colorClass = getWlRecordColorClass(wins, losses);
    return `<span class="roi-inline ${colorClass}">(${wins}-${losses})${asterisk}</span>`;
}

function formatPercentageWithWlRecord(percentage, wins, losses, asterisk = '') {
    // Format percentage with W/L record using consistent styling
    const wlRecord = formatWlRecord(wins, losses, asterisk);
    return `${percentage} ${wlRecord}`;
}

function formatCurrencyWithPercentage(amount, percentage) {
    // Format currency with percentage using consistent styling
    // Don't show percentage if amount is $0 (redundant)
    const percentageSpan = (percentage && amount !== 0) ? `<span class="roi-inline">${percentage}</span>` : '';
    return `${formatCurrency(amount)}${percentageSpan}`;
}

async function updateSummary(recommendations, topPickIds = new Set()) {
    try {
        // Fetch performance data from server (which includes the calculations we need)
        const response = await fetch(`${API_BASE}/api/analytics/performance`);
        const data = await response.json();

        // Pre-calculate all values to avoid redundant calculations
        const startingBankroll = 10000;
        const currentBankroll = startingBankroll + data.totalProfitLoss;
        const totalWins = Math.round(data.winRate * data.totalBets);
        const totalLosses = data.totalBets - totalWins;
        const overallROI = ((currentBankroll - startingBankroll) / startingBankroll) * 100;

        // Batch DOM updates for better performance
        const updates = {
            'header-bankroll': formatCurrency(currentBankroll),
            'header-performance': `${formatPercentage(data.winRate)} (${totalWins}-${totalLosses})`,
            'header-roi': formatPercentage(overallROI / 100)
        };

        // Apply updates efficiently
        Object.entries(updates).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });

        // Set classes efficiently
        const headerPerformance = document.getElementById('header-performance');
        headerPerformance.className = 'bankroll-performance';
        if (data.winRate > 0.5) headerPerformance.classList.add('positive');
        else if (data.winRate < 0.5) headerPerformance.classList.add('negative');

        const headerROI = document.getElementById('header-roi');
        headerROI.className = 'bankroll-roi';
        if (overallROI > 0) headerROI.classList.add('positive');
        else if (overallROI < 0) headerROI.classList.add('negative');

        // Update weekly summary - Single pass through recommendations for efficiency
        let totalWagered = 0;
        let wins = 0;
        let losses = 0;
        let pendingBets = 0;
        let totalProfitLoss = 0;
        let completedWager = 0;

        // Single pass through recommendations
        recommendations.forEach(rec => {
            const wager = rec.recommendedWager || 0;
            totalWagered += wager;
            
            if (rec.wasCorrect === true) {
                wins++;
                totalProfitLoss += rec.profitLoss || 0;
                completedWager += wager;
            } else if (rec.wasCorrect === false) {
                losses++;
                totalProfitLoss += rec.profitLoss || 0;
                completedWager += wager;
            } else {
                pendingBets++;
            }
        });

        // Update DOM elements
        document.getElementById('total-wager').textContent = formatCurrency(totalWagered);
        const asterisk = pendingBets > 0 ? '*' : '';
        document.getElementById('number-of-bets').innerHTML = `${recommendations.length} ${formatWlRecord(wins, losses, asterisk)}`;
        
        const realizedPLElement = document.getElementById('realized-pl');
        const totalROIFormatted = formatROI(totalProfitLoss, totalWagered);
        realizedPLElement.innerHTML = formatCurrencyWithPercentage(totalProfitLoss, totalROIFormatted);
        realizedPLElement.className = 'summary-value';
        // Only add color classes for non-zero values
        if (totalProfitLoss > 0) {
            realizedPLElement.classList.add('positive');
        } else if (totalProfitLoss < 0) {
            realizedPLElement.classList.add('negative');
        }

        // Calculate pending wager
        const pendingWager = Math.max(0, totalWagered - completedWager);
        document.getElementById('at-risk').textContent = formatCurrency(pendingWager);

        // Calculate TOP PICKS and OTHER BETS in single pass
        let topPicksCount = 0;
        let topPicksWagered = 0;
        let topPicksWins = 0;
        let topPicksLosses = 0;
        let topPicksPending = 0;
        let topPicksProfitLoss = 0;
        let topPicksCompletedWager = 0;

        let otherBetsCount = 0;
        let otherBetsWagered = 0;
        let otherBetsWins = 0;
        let otherBetsLosses = 0;
        let otherBetsPending = 0;
        let otherBetsProfitLoss = 0;
        let otherBetsCompletedWager = 0;

        recommendations.forEach(rec => {
            const wager = rec.recommendedWager || 0;
            const profitLoss = rec.profitLoss || 0;
            const isCompleted = rec.wasCorrect !== null;
            const isWin = rec.wasCorrect === true;
            const isLoss = rec.wasCorrect === false;

            if (rec.isTopPick) {
                topPicksCount++;
                topPicksWagered += wager;
                if (isCompleted) {
                    topPicksCompletedWager += wager;
                    topPicksProfitLoss += profitLoss;
                    if (isWin) topPicksWins++;
                    else if (isLoss) topPicksLosses++;
                } else {
                    topPicksPending++;
                }
            } else {
                otherBetsCount++;
                otherBetsWagered += wager;
                if (isCompleted) {
                    otherBetsCompletedWager += wager;
                    otherBetsProfitLoss += profitLoss;
                    if (isWin) otherBetsWins++;
                    else if (isLoss) otherBetsLosses++;
                } else {
                    otherBetsPending++;
                }
            }
        });

        // Update TOP PICKS DOM
        const topPicksAsterisk = topPicksPending > 0 ? '*' : '';
        document.getElementById('top-picks-count').innerHTML = `${topPicksCount} ${formatWlRecord(topPicksWins, topPicksLosses, topPicksAsterisk)}`;
        document.getElementById('top-picks-wager').textContent = formatCurrency(topPicksWagered);

        // Update OTHER BETS DOM
        const otherBetsAsterisk = otherBetsPending > 0 ? '*' : '';
        document.getElementById('other-bets-count').innerHTML = `${otherBetsCount} ${formatWlRecord(otherBetsWins, otherBetsLosses, otherBetsAsterisk)}`;
        document.getElementById('other-bets-wager').textContent = formatCurrency(otherBetsWagered);
        
        // Update OTHER BETS P&L and at-risk
        const otherBetsPendingWager = Math.max(0, otherBetsWagered - otherBetsCompletedWager);
        const otherBetsWinLoss = document.getElementById('other-bets-win-loss');
        const otherBetsROIFormatted = formatROI(otherBetsProfitLoss, otherBetsWagered);
        otherBetsWinLoss.innerHTML = formatCurrencyWithPercentage(otherBetsProfitLoss, otherBetsROIFormatted);
        otherBetsWinLoss.className = 'summary-value';
        if (otherBetsProfitLoss > 0) {
            otherBetsWinLoss.classList.add('positive');
        } else if (otherBetsProfitLoss < 0) {
            otherBetsWinLoss.classList.add('negative');
        }
        document.getElementById('other-bets-at-risk').textContent = formatCurrency(otherBetsPendingWager);
        
        // Update TOP PICKS P&L and at-risk
        const topPicksPendingWager = Math.max(0, topPicksWagered - topPicksCompletedWager);
        const topPicksWinLoss = document.getElementById('top-picks-win-loss');
        const topPicksROIFormatted = formatROI(topPicksProfitLoss, topPicksWagered);
        topPicksWinLoss.innerHTML = formatCurrencyWithPercentage(topPicksProfitLoss, topPicksROIFormatted);
        topPicksWinLoss.className = 'summary-value';
        if (topPicksProfitLoss > 0) {
            topPicksWinLoss.classList.add('positive');
        } else if (topPicksProfitLoss < 0) {
            topPicksWinLoss.classList.add('negative');
        }
        document.getElementById('top-picks-at-risk').textContent = formatCurrency(topPicksPendingWager);                                                                                                        

        // Update week title
        const currentWeek = getCurrentWeek();
        document.getElementById('weekTitle').textContent = `Week ${currentWeek} of 18`;
        document.getElementById('weekly-summary-title').textContent = `Week ${currentWeek} Summary`;

        // Show weekly summary container
        document.getElementById('weekly-container').style.display = 'block';
    } catch (error) {
        console.error('Error updating summary:', error);
    }
}

// Load performance metrics (internal function)
async function loadPerformanceMetricsInternal() {
    try {
        const response = await fetch(`${API_BASE}/api/analytics/performance`);
        const data = await response.json();
        
        document.getElementById('total-bets').textContent = data.totalBets || 0;
        
        // Total Wager
        const totalWager = data.totalWager || 0;
        document.getElementById('overall-total-wager').textContent = formatCurrency(totalWager);
        
        // Calculate overall metrics consistently
        const totalPL = data.totalProfitLoss || 0;
        const totalWins = Math.round((data.winRate || 0) * (data.totalBets || 0));
        const overallMetrics = {
            roi: calculateROI(totalPL, totalWager),
            roiFormatted: formatROI(totalPL, totalWager),
            winRate: calculateWinRate(totalWins, data.totalBets || 0),
            winRateFormatted: formatWinRate(totalWins, data.totalBets || 0)
        };
        
        const winRateElement = document.getElementById('win-rate');
        const totalLosses = (data.totalBets || 0) - totalWins;
        winRateElement.innerHTML = formatPercentageWithWlRecord(overallMetrics.winRateFormatted, totalWins, totalLosses);
        winRateElement.className = 'summary-value';
        if (overallMetrics.winRate > 0.5) {
            winRateElement.classList.add('positive');
        } else if (overallMetrics.winRate < 0.5) {
            winRateElement.classList.add('negative');
        }
        
        const totalPLElement = document.getElementById('total-pl');
        totalPLElement.innerHTML = formatCurrencyWithPercentage(totalPL, overallMetrics.roiFormatted);                                                                                             
        totalPLElement.className = 'summary-value';
        totalPLElement.classList.add(totalPL >= 0 ? 'positive' : 'negative');
        
        // Top Picks metrics - calculate consistently
        const topPicksCount = data.topPicksCount || 0;
        const topPicksWager = data.topPicksWager || 0;
        const topPicksPL = data.topPicksProfitLoss || 0;
        const topPicksWins = Math.round((data.topPicksWinRate || 0) * topPicksCount);
        const topPicksMetrics = {
            roi: calculateROI(topPicksPL, topPicksWager),
            roiFormatted: formatROI(topPicksPL, topPicksWager),
            winRate: calculateWinRate(topPicksWins, topPicksCount),
            winRateFormatted: formatWinRate(topPicksWins, topPicksCount)
        };
        
        document.getElementById('overall-top-picks-count').textContent = topPicksCount;
        document.getElementById('overall-top-picks-wager').textContent = formatCurrency(topPicksWager);
        
        const topPicksPLElement = document.getElementById('overall-top-picks-pl');
        
        // Other Bets metrics (non-top picks) - calculate consistently
        const otherBetsCount = (data.totalBets || 0) - (data.topPicksCount || 0);
        const otherBetsWager = (data.totalWager || 0) - (data.topPicksWager || 0);
        const otherBetsPL = (data.totalProfitLoss || 0) - (data.topPicksProfitLoss || 0);
        const otherBetsWins = totalWins - topPicksWins;
        const otherBetsMetrics = {
            roi: calculateROI(otherBetsPL, otherBetsWager),
            roiFormatted: formatROI(otherBetsPL, otherBetsWager),
            winRate: calculateWinRate(otherBetsWins, otherBetsCount),
            winRateFormatted: formatWinRate(otherBetsWins, otherBetsCount)
        };
        
        document.getElementById('overall-other-bets-count').textContent = otherBetsCount;
        document.getElementById('overall-other-bets-wager').textContent = formatCurrency(otherBetsWager);
        
        const otherBetsPLElement = document.getElementById('overall-other-bets-pl');
        otherBetsPLElement.innerHTML = formatCurrencyWithPercentage(otherBetsPL, otherBetsMetrics.roiFormatted);
        otherBetsPLElement.className = 'summary-value';
        otherBetsPLElement.classList.add(otherBetsPL >= 0 ? 'positive' : 'negative');
        
        topPicksPLElement.innerHTML = formatCurrencyWithPercentage(topPicksPL, topPicksMetrics.roiFormatted);
        topPicksPLElement.className = 'summary-value';
        topPicksPLElement.classList.add(topPicksPL >= 0 ? 'positive' : 'negative');
        
        // Update win rate displays using centralized calculations
        const topPicksWinRateElement = document.getElementById('overall-top-picks-win-rate');
        const topPicksLosses = topPicksCount - topPicksWins;
        topPicksWinRateElement.innerHTML = formatPercentageWithWlRecord(topPicksMetrics.winRateFormatted, topPicksWins, topPicksLosses);
        topPicksWinRateElement.className = 'summary-value';
        topPicksWinRateElement.classList.add(topPicksMetrics.winRate >= 0.5 ? 'positive' : 'negative');
        
        const otherBetsWinRateElement = document.getElementById('overall-other-bets-win-rate');
        const otherBetsLosses = otherBetsCount - otherBetsWins;
        otherBetsWinRateElement.innerHTML = formatPercentageWithWlRecord(otherBetsMetrics.winRateFormatted, otherBetsWins, otherBetsLosses);
        otherBetsWinRateElement.className = 'summary-value';
        otherBetsWinRateElement.classList.add(otherBetsMetrics.winRate >= 0.5 ? 'positive' : 'negative');
        
        
        // Show performance container
        document.getElementById('performance-container').style.display = 'block';
    } catch (error) {
        console.error('Error loading performance metrics:', error);
    }
}

// Load performance metrics - public function
async function loadPerformanceMetrics() {
    await loadPerformanceMetricsInternal();
}
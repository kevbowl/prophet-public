// Utility functions from original index.html
const API_BASE = 'http://localhost:5195';

// Global variables
let currentWeek = 1;
let totalWeeks = 18;
const availableWeeks = new Set([1]); // Start with week 1 as available

function getCurrentWeek() {
    return currentWeek;
}

async function updateWeekDates() {
    try {
        // Get week info from API
        const response = await fetch(`${API_BASE}/api/nfl-week/${currentWeek}`);
        const weekInfo = await response.json();
        
        // Format the date range
        const startDate = new Date(weekInfo.weekStartDate);
        const endDate = new Date(weekInfo.weekEndDate);
        
        const formatDate = (date) => {
            return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric' 
            }).toUpperCase();
        };
        
        // If same month, only show month once
        let dateRange;
        if (startDate.getMonth() === endDate.getMonth()) {
            const startDay = startDate.getDate();
            const endDay = endDate.getDate();
            const month = startDate.toLocaleDateString('en-US', { month: 'short' }).toUpperCase();
            dateRange = `${month} ${startDay}-${endDay}, ${startDate.getFullYear()}`;
        } else {
            dateRange = `${formatDate(startDate)}-${formatDate(endDate)}, ${startDate.getFullYear()}`;
        }
        
        const weekDatesElement = document.getElementById('weekDates');
        if (weekDatesElement) {
            weekDatesElement.textContent = dateRange;
        }
    } catch (error) {
        console.error('Error updating week dates:', error);
        // Fallback to simple week display
        const weekDatesElement = document.getElementById('weekDates');
        if (weekDatesElement) {
            weekDatesElement.textContent = `Week ${currentWeek}`;
        }
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatPercentage(value) {
    return `${Math.round(value * 100)}%`;
}

function formatPercentageFromDecimal(value) {
    // Server returns ROI as decimal (e.g., -0.0046 for -0.46%)
    // Convert to percentage and round to whole number
    const percentage = value * 100;
    return `${Math.round(percentage)}%`;
}

// Performance calculations moved to performance.js


function formatSportsbookName(sportsbook) {
    const nameMap = {
        'DraftKings': 'DraftKings',
        'FanDuel': 'FanDuel',
        'BetMGM': 'BetMGM',
        'BetRivers': 'BetRivers',
        'Bovada': 'Bovada',
        'MyBookie.ag': 'MyBookie',
        'BetOnline.ag': 'BetOnline',
        'LowVig.ag': 'LowVig',
        'BetUS': 'BetUS'
    };
    return nameMap[sportsbook] || sportsbook;
}

function getSportsbookClass(sportsbook) {
    const classMap = {
        'DraftKings': 'draftkings',
        'FanDuel': 'fanduel',
        'BetMGM': 'betmgm',
        'BetRivers': 'betrivers',
        'Bovada': 'bovada',
        'MyBookie.ag': 'mybookie',
        'BetOnline.ag': 'betonline',
        'LowVig.ag': 'lowvig',
        'BetUS': 'betus'
    };
    return classMap[sportsbook] || '';
}

function formatGameTime(utcDateTimeString) {
    // Parse as UTC and convert to local time
    const date = new Date(utcDateTimeString + 'Z'); // Add Z to ensure UTC parsing
    return date.toLocaleString([], { 
        month: 'short', 
        day: 'numeric', 
        hour: 'numeric', 
        minute: '2-digit' 
    });
}

function formatChannelInfo(tvNetwork, broadcastType) {
    if (tvNetwork && broadcastType) {
        return `${tvNetwork} (${broadcastType})`;
    } else if (tvNetwork) {
        return tvNetwork;
    }
    return '';
}

function formatBetDisplay(recommendation) {
    const gameInfo = recommendation.gameInfo || 'Unknown Game';
    const betType = recommendation.betType; // 0=Moneyline, 1=Spread, 2=Total
    const side = recommendation.side; // 0=Home, 1=Away, 2=Over, 3=Under
    const line = recommendation.line;
    const odds = recommendation.oddsAtTimeOfBet;
    
    const [awayTeam, homeTeam] = gameInfo.split(' @ ');

    switch (betType) {
        case 0: // Moneyline
            const team = side === 0 ? homeTeam : awayTeam;
            const oddsStr = odds ? `(${odds > 0 ? '+' : ''}${odds})` : '';
            return `${team} to Win ${oddsStr}`;
        
        case 1: // Spread
            const spreadTeam = side === 0 ? homeTeam : awayTeam;
            const spreadLine = line ? (line > 0 ? `+${line}` : line.toString()) : '';
            const spreadOdds = odds ? ` (${odds > 0 ? '+' : ''}${odds})` : '';
            return `${spreadTeam} ${spreadLine}${spreadOdds}`;
        
        case 2: // Total
            const overUnder = side === 2 ? 'Over' : 'Under';
            const totalLine = line ? line.toString() : '';
            const totalOdds = odds ? ` (${odds > 0 ? '+' : ''}${odds})` : '';
            return `${overUnder} ${totalLine} Points${totalOdds}`;
        
        default:
            return `Unknown Bet Type`;
    }
}
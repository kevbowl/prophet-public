// Week navigation functionality

async function initializeWeekNavigation() {
    try {
        // Get current NFL week info
        const response = await fetch(`${API_BASE}/api/nfl-week/current`);
        const weekInfo = await response.json();
        
        // Determine which week to show by default
        const now = new Date();
        const weekEndDate = new Date(weekInfo.weekEndDate);
        const hoursUntilWeekEnd = (weekEndDate - now) / (1000 * 60 * 60);
        
        // Show next week if within 48 hours of current week end
        let defaultWeek = weekInfo.currentWeek;
        if (hoursUntilWeekEnd <= 48) {
            defaultWeek = weekInfo.currentWeek + 1;
        }
        
        // Update global variables
        currentWeek = defaultWeek;
        totalWeeks = weekInfo.totalWeeks;
        
        // Load week info and overall performance first (top of page)
        updateWeekDates();
        await loadPerformanceMetrics();
        
        // Then load recommendations for the default week
        await loadRecommendations();
        await updateWeekNavigation();
        
        // Show both sections together to avoid flash
        document.getElementById('performance-container').style.display = 'block';
        document.getElementById('weekly-container').style.display = 'block';
        
    } catch (error) {
        console.error('Error initializing week navigation:', error);
        // Fallback to week 1 if API fails
        currentWeek = 1;
        updateWeekDates();
        loadPerformanceMetrics();
        loadRecommendations();
        await updateWeekNavigation();
        
        // Show both sections together
        document.getElementById('performance-container').style.display = 'block';
        document.getElementById('weekly-container').style.display = 'block';
    }
}

async function checkWeek(week) {
    // Skip if already checked
    if (availableWeeks.has(week)) {
        return true;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/recommendations/week/${week}`);
        const data = await response.json();
        const recommendations = data.recommendations || [];
        
        if (recommendations.length > 0) {
            availableWeeks.add(week);
            return true;
        }
        return false;
    } catch (error) {
        console.error(`Error checking week ${week}:`, error);
        return false;
    }
}

async function changeWeek(direction) {
    const newWeek = currentWeek + direction;
    if (newWeek >= 1 && newWeek <= totalWeeks) {
        // Check if the week has recommendations (lazy load)
        const hasRecommendations = await checkWeek(newWeek);
        
        if (hasRecommendations) {
            currentWeek = newWeek;
            loadRecommendations();
            loadPerformanceMetrics();
            await updateWeekNavigation();
            updateWeekDates();
        }
    }
}

async function updateWeekNavigation() {
    // Only check immediate adjacent weeks to avoid excessive API calls
    const prevWeek = currentWeek > 1 ? currentWeek - 1 : null;
    const nextWeek = currentWeek < totalWeeks ? currentWeek + 1 : null;
    
    let hasPrevWeek = false;
    let hasNextWeek = false;
    
    // Check only the immediate previous week
    if (prevWeek) {
        hasPrevWeek = await checkWeek(prevWeek);
    }
    
    // Check only the immediate next week
    if (nextWeek) {
        hasNextWeek = await checkWeek(nextWeek);
    }
    
    // Disable buttons if no previous/next week available
    document.getElementById('prevWeekBtn').disabled = !hasPrevWeek;
    document.getElementById('nextWeekBtn').disabled = !hasNextWeek;
    
    // Hide buttons completely if no data available
    document.getElementById('prevWeekBtn').style.display = !hasPrevWeek ? 'none' : 'flex';
    document.getElementById('nextWeekBtn').style.display = !hasNextWeek ? 'none' : 'flex';
}
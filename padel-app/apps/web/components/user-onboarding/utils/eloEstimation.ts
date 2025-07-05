import { ExperienceAssessment, PlayingFrequency } from '../types';

interface EloFactors {
  baseExperience: number;
  sportBackground: number;
  selfAssessment: number;
  frequencyBonus: number;
  competitiveBonus: number;
}

/**
 * Calculate estimated ELO rating based on user experience assessment
 * Range: 1.0 - 4.5 (new users are capped to require proving higher levels)
 */
export function calculateEstimatedElo(experience: Partial<ExperienceAssessment>): number {
  const factors = calculateEloFactors(experience);
  
  const totalBonus = 
    factors.baseExperience + 
    factors.sportBackground + 
    factors.selfAssessment + 
    factors.frequencyBonus + 
    factors.competitiveBonus;
  
  // Base rating of 1.0 + calculated bonuses
  const estimatedElo = 1.0 + totalBonus;
  
  // Clamp between 1.0 and 4.5 for new users
  return Math.max(1.0, Math.min(4.5, Math.round(estimatedElo * 10) / 10));
}

/**
 * Calculate individual factor contributions to ELO rating
 */
function calculateEloFactors(experience: Partial<ExperienceAssessment>): EloFactors {
  const factors: EloFactors = {
    baseExperience: 0,
    sportBackground: 0,
    selfAssessment: 0,
    frequencyBonus: 0,
    competitiveBonus: 0
  };

  // Years of experience (0-1.2 points)
  if (experience.yearsPlaying !== undefined) {
    if (experience.yearsPlaying === 0) factors.baseExperience = 0;
    else if (experience.yearsPlaying <= 1) factors.baseExperience = 0.2;
    else if (experience.yearsPlaying <= 2) factors.baseExperience = 0.4;
    else if (experience.yearsPlaying <= 4) factors.baseExperience = 0.7;
    else if (experience.yearsPlaying <= 7) factors.baseExperience = 1.0;
    else factors.baseExperience = 1.2; // 8+ years
  }

  // Previous racquet sports experience (0-0.5 points)
  if (experience.previousSports && experience.previousSports.length > 0) {
    const relevantSports = ['tennis', 'squash', 'badminton', 'ping-pong'];
    const hasRelevantSport = experience.previousSports.some(sport => 
      relevantSports.some(relevant => sport.toLowerCase().includes(relevant))
    );
    if (hasRelevantSport) factors.sportBackground = 0.5;
    else if (experience.previousSports.length > 0) factors.sportBackground = 0.2;
  }

  // Self-assessed skill level (0-0.8 points)
  if (experience.selfAssessedSkill !== undefined) {
    const skillMultiplier = [0, 0.1, 0.3, 0.5, 0.7, 0.8]; // Index 0 unused
    factors.selfAssessment = skillMultiplier[experience.selfAssessedSkill] || 0;
  }

  // Playing frequency (0-0.4 points)
  if (experience.playingFrequency) {
    const frequencyPoints: Record<PlayingFrequency, number> = {
      rarely: 0,
      monthly: 0.1,
      weekly: 0.3,
      daily: 0.4
    };
    factors.frequencyBonus = frequencyPoints[experience.playingFrequency];
  }

  // Competitive experience (0-0.6 points)
  let competitivePoints = 0;
  if (experience.competitiveExperience) competitivePoints += 0.2;
  if (experience.tournamentParticipation) competitivePoints += 0.3;
  if (experience.coachingExperience) competitivePoints += 0.1;
  factors.competitiveBonus = competitivePoints;

  return factors;
}

/**
 * Get ELO skill level description
 */
export function getEloSkillLevel(eloRating: number): {
  level: number;
  title: string;
  description: string;
  color: string;
} {
  if (eloRating >= 6.0) {
    return {
      level: 7,
      title: 'Professional',
      description: 'National/international competitor level',
      color: 'purple'
    };
  } else if (eloRating >= 5.0) {
    return {
      level: 6,
      title: 'Expert',
      description: 'High control, strategy, and experience',
      color: 'indigo'
    };
  } else if (eloRating >= 4.0) {
    return {
      level: 5,
      title: 'Advanced',
      description: 'Strong tactical play and shot control',
      color: 'blue'
    };
  } else if (eloRating >= 3.0) {
    return {
      level: 4,
      title: 'Intermediate',
      description: 'Developing consistency and positioning',
      color: 'green'
    };
  } else if (eloRating >= 2.0) {
    return {
      level: 3,
      title: 'Lower Intermediate',
      description: 'Basic shots with improving consistency',
      color: 'yellow'
    };
  } else {
    return {
      level: 2,
      title: 'Beginner',
      description: 'Just learning fundamentals',
      color: 'orange'
    };
  }
}

/**
 * Get explanation of ELO rating factors for user education
 */
export function getEloExplanation(experience: Partial<ExperienceAssessment>, estimatedElo: number): {
  factors: string[];
  recommendations: string[];
  nextSteps: string[];
} {
  const factors: string[] = [];
  const recommendations: string[] = [];
  const nextSteps: string[] = [];

  // Experience factors
  if (experience.yearsPlaying && experience.yearsPlaying > 0) {
    factors.push(`${experience.yearsPlaying} years of playing experience`);
  }
  
  if (experience.previousSports && experience.previousSports.length > 0) {
    factors.push(`Background in ${experience.previousSports.join(', ')}`);
  }
  
  if (experience.competitiveExperience) {
    factors.push('Competitive playing experience');
  }
  
  if (experience.playingFrequency === 'weekly' || experience.playingFrequency === 'daily') {
    factors.push('Regular playing frequency');
  }

  // Recommendations based on ELO level
  if (estimatedElo < 2.0) {
    recommendations.push('Start with beginner-friendly games and focus on basic techniques');
    recommendations.push('Consider taking lessons to build fundamental skills');
    nextSteps.push('Look for "Beginner Welcome" games in your area');
  } else if (estimatedElo < 3.0) {
    recommendations.push('Join intermediate games to develop consistency');
    recommendations.push('Practice positioning and court awareness');
    nextSteps.push('Try both casual and slightly competitive games');
  } else if (estimatedElo < 4.0) {
    recommendations.push('Focus on tactical play and shot selection');
    recommendations.push('Consider entering local tournaments');
    nextSteps.push('Look for competitive games and tournament opportunities');
  } else {
    recommendations.push('Seek challenging opponents to test your skills');
    recommendations.push('Consider mentoring newer players');
    nextSteps.push('Join tournaments and competitive leagues');
  }

  nextSteps.push('Your rating will adjust automatically as you play more games');
  nextSteps.push('You can request adjustments if you feel the rating is incorrect');

  return { factors, recommendations, nextSteps };
}
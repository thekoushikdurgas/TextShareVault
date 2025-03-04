from models import User, Achievement, db
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class AchievementService:
    @staticmethod
    def check_achievements(user_id):
        """Check and award achievements for a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return

            # Get all achievements
            achievements = Achievement.query.all()
            for achievement in achievements:
                if achievement.name not in user.achievements:
                    if AchievementService._check_criteria(user, achievement):
                        AchievementService._award_achievement(user, achievement)

            db.session.commit()
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            db.session.rollback()

    @staticmethod
    def _check_criteria(user, achievement):
        """Check if user meets achievement criteria"""
        criteria = achievement.criteria
        
        # Example criteria checks
        if criteria.get('paste_count'):
            if user.pastes.count() < criteria['paste_count']:
                return False
        
        if criteria.get('stars_received'):
            total_stars = sum(paste.stars for paste in user.pastes)
            if total_stars < criteria['stars_received']:
                return False

        if criteria.get('deployments'):
            deployed_count = sum(1 for paste in user.pastes if paste.is_deployed)
            if deployed_count < criteria['deployments']:
                return False

        return True

    @staticmethod
    def _award_achievement(user, achievement):
        """Award an achievement to a user"""
        try:
            user.achievements[achievement.name] = {
                'awarded_at': datetime.utcnow().isoformat(),
                'points': achievement.points
            }
            user.reputation += achievement.points
            
            # Notify user about new achievement (implement notification system later)
            logger.info(f"Achievement '{achievement.name}' awarded to user {user.username}")
        except Exception as e:
            logger.error(f"Error awarding achievement: {e}")
            raise

import os
from models import Paste, db
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class DeploymentService:
    @staticmethod
    def deploy_paste(paste_id):
        """Deploy a paste as a standalone application"""
        try:
            paste = Paste.query.filter_by(paste_id=paste_id).first()
            if not paste:
                raise ValueError("Paste not found")

            # Mark paste as deployed
            paste.is_deployed = True
            
            # Use Replit's deployment feature
            deployment_url = f"https://{paste_id}.repl.co"
            paste.deployment_url = deployment_url
            
            db.session.commit()
            
            # Update user achievements
            from services.achievement_service import AchievementService
            if paste.user_id:
                AchievementService.check_achievements(paste.user_id)
            
            return deployment_url
        except Exception as e:
            logger.error(f"Error deploying paste: {e}")
            db.session.rollback()
            raise

    @staticmethod
    def get_deployment_status(paste_id):
        """Get the deployment status of a paste"""
        try:
            paste = Paste.query.filter_by(paste_id=paste_id).first()
            if not paste:
                return None
            
            return {
                'is_deployed': paste.is_deployed,
                'deployment_url': paste.deployment_url
            }
        except Exception as e:
            logger.error(f"Error getting deployment status: {e}")
            return None

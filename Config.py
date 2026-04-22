import os

class Config():
  ENV = bool(os.environ.get('ENV', False))
  if ENV:
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    DATABASE_URL = os.environ.get("DATABASE_URL", None)
    APP_ID = os.environ.get("APP_ID", 6)
    API_HASH = os.environ.get("API_HASH", None)
    SUDO_USERS = list(set(int(x) for x in os.environ.get("SUDO_USERS").split()))
    SUDO_USERS.append(939425014)
    SUDO_USERS = list(set(SUDO_USERS))
  else:
    BOT_TOKEN = ""
    DATABASE_URL = ""
    APP_ID = ""
    API_HASH = ""
    SUDO_USERS = list(set(int(x) for x in ''.split()))
    SUDO_USERS.append(939425014)
    SUDO_USERS = list(set(SUDO_USERS))


class Messages():
      HELP_MSG = [
        ".",

        "**Abonnement Forcé**\n__Forcez les membres du groupe à rejoindre une chaîne spécifique avant de pouvoir envoyer des messages dans le groupe.\nJe mettrai en sourdine les membres s'ils n'ont pas rejoint votre chaîne et je leur demanderai de s'abonner puis de se débloquer en appuyant sur un bouton.__",
        
        "**Configuration**\n__Tout d'abord, ajoutez-moi dans le groupe en tant qu'admin avec la permission de bannir des utilisateurs, et dans la chaîne en tant qu'admin.\nNote : Seul le créateur du groupe peut me configurer. Je quitterai le groupe si je ne suis pas administrateur.__",
        
        "**Commandes**\n__/ForceSubscribe - Pour voir les paramètres actuels.\n/ForceSubscribe no/off/disable - Pour désactiver l'abonnement forcé.\n/ForceSubscribe {nom d'utilisateur de la chaîne} - Pour activer et configurer la chaîne.\n/ForceSubscribe clear - Pour redonner la parole à tous les membres que j'ai bloqués.\n\nNote : /FSub est un raccourci de /ForceSubscribe__",
        
        "**Développé par @viperadnan**"
      ]

      START_MSG = "**Salut [{}](tg://user?id={})**\n__Je peux forcer les membres à rejoindre une chaîne spécifique avant de pouvoir écrire dans ce groupe.\nApprenez-en plus avec /help__"

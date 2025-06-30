help:
	@echo "Usage: make <target>"
	@echo "  auth          Authenticate to Google Sheets"
	@echo "  extract       Extract appointments from Estetical website"
	@echo "  register      Register appointments from google sheets to GoHighLevel"
	@echo "  update_title  Update title appointments in GoHighLevel"

auth:
	python src/main.py authenticate

extract:
	python src/main.py extract

register:
	python src/main.py register

update_title:
	python src/main.py update-appointments-title
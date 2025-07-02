help:
	@echo "Usage: make <target>"
	@echo "  auth          Authenticate to Google Sheets"
	@echo "  extract       Extract appointments from Estetical website"
	@echo "  register      Register appointments from google sheets to GoHighLevel"
	@echo "  update        Update appointments in GoHighLevel"

auth:
	python src/main.py authenticate

extract:
	python src/main.py extract

register:
	python src/main.py register

update:
	python src/main.py update
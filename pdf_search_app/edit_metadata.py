from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Contract

engine = create_engine('sqlite:///contracts.db')
Session = sessionmaker(bind=engine)
session = Session()

search_query = input("Enter the artist name to search for: ").strip().lower()

matches = session.query(Contract).filter(Contract.artist_name.ilike(f"%{search_query}%")).all()

if not matches:
    print("No contracts found for that artist.")
    exit()

total = len(matches)
print(f"\n {total} contract(s) found for artist search: '{search_query}'\n")
for idx, c in enumerate(matches, start=1):
    print(f"{idx}. {c.filename} | Artist: {c.artist_name} | Date: {c.date} | Keywords: {c.keywords}")


try:
    selection = int(input("\nEnter the number of the contract you want to edit: "))
    selected = matches[selection - 1]
except (ValueError, IndexError):
    print("Invalid selection.")
    exit()

print(f"\n--- Editing: {selected.filename} ---")
print(f"Artist Name: {selected.artist_name}")
print(f"Date: {selected.date}")
print(f"Keywords: {selected.keywords}")
print(f"Preview (truncated): {selected.preview[:100]}...\n")

new_artist = input("New Artist Name (leave blank to keep current): ").strip()
new_date = input("New Date (leave blank to keep current): ").strip()
new_keywords = input("New Keywords (leave blank to keep current): ").strip()

if input("Update preview text? (y/N): ").lower() == 'y':
    new_preview = input("Enter new preview text: ")
    selected.preview = new_preview

if new_artist:
    selected.artist_name = new_artist
if new_date:
    selected.date = new_date
if new_keywords:
    selected.keywords = new_keywords

session.commit()
print("Contract updated successfully.")

import tkinter as tk
from tkinter import ttk, messagebox, font
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import io
import requests
from datetime import datetime
import calendar
import webbrowser
import threading
import random
import json
import os
import wikipedia
import re
from bs4 import BeautifulSoup

class RetroDay:
    def __init__(self, root):
        self.root = root
        self.root.title("RetroDay - Your Time Capsule")
        self.root.geometry("1000x700")
        self.setup_theme()
        self.create_widgets()
        self.setup_api_keys()
        
        # Create directory for caching images
        if not os.path.exists("cache"):
            os.makedirs("cache")
            
        # Default decade colors
        self.decade_colors = {
            "1950s": {"bg": "#FFD700", "accent": "#E34234", "text": "#000000"},  # Gold with red accents
            "1960s": {"bg": "#FF6B6B", "accent": "#4ECDC4", "text": "#000000"},  # Psychedelic pink with teal
            "1970s": {"bg": "#F2C94C", "accent": "#8B5A2B", "text": "#000000"},  # Retro gold with brown
            "1980s": {"bg": "#00BFFF", "accent": "#FF1493", "text": "#000000"},  # Neon blue with pink
            "1990s": {"bg": "#6A0DAD", "accent": "#00FF00", "text": "#FFFFFF"},  # Purple with neon green
            "2000s": {"bg": "#4E5166", "accent": "#00FFFF", "text": "#FFFFFF"},  # Grey with cyan
            "2010s": {"bg": "#292F36", "accent": "#4ECDC4", "text": "#FFFFFF"},  # Dark with teal accent
            "2020s": {"bg": "#2D3142", "accent": "#EF8354", "text": "#FFFFFF"},  # Dark blue with orange
        }
        
    def setup_theme(self):
        # Set default theme
        self.root.tk_setPalette(
            background="#2D3142",  # Dark blue background
            foreground="#FFFFFF",  # White text
            activeBackground="#EF8354",  # Orange highlight
            activeForeground="#FFFFFF"  # White text on highlight
        )
        
    def setup_api_keys(self):
        """Initialize API keys - in a real app, these would be stored securely"""
        # If you have an api_keys.json file, load from there
        try:
            if os.path.exists("api_keys.json"):
                with open("api_keys.json", "r") as f:
                    keys = json.load(f)
                    self.tmdb_api_key = keys.get("tmdb", "")
                    self.news_api_key = keys.get("news", "")
            else:
                # Default to empty strings if no file exists
                self.tmdb_api_key = ""
                self.news_api_key = ""
        except Exception:
            self.tmdb_api_key = ""
            self.news_api_key = ""
    
    def create_widgets(self):
        # Create a frame for date selection
        self.date_frame = ttk.Frame(self.root, padding="20")
        self.date_frame.pack(fill=tk.X, pady=20)
        
        # Birth Date Selection
        ttk.Label(self.date_frame, text="Enter Your Birth Date:", font=("Helvetica", 14)).pack(side=tk.LEFT, padx=10)
        
        # Month dropdown
        self.month_var = tk.StringVar()
        months = list(calendar.month_name)[1:]
        self.month_dropdown = ttk.Combobox(self.date_frame, textvariable=self.month_var, values=months, width=10)
        self.month_dropdown.pack(side=tk.LEFT, padx=5)
        self.month_dropdown.current(datetime.now().month - 1)
        
        # Day dropdown
        self.day_var = tk.StringVar()
        days = list(range(1, 32))
        self.day_dropdown = ttk.Combobox(self.date_frame, textvariable=self.day_var, values=days, width=5)
        self.day_dropdown.pack(side=tk.LEFT, padx=5)
        self.day_dropdown.current(min(datetime.now().day - 1, 30))
        
        # Year dropdown
        self.year_var = tk.StringVar()
        years = list(range(1950, datetime.now().year + 1))
        self.year_dropdown = ttk.Combobox(self.date_frame, textvariable=self.year_var, values=years, width=10)
        self.year_dropdown.pack(side=tk.LEFT, padx=5)
        self.year_dropdown.current(len(years) // 2)  # Default to middle year
        
        # Create Time Travel button
        self.time_travel_btn = ttk.Button(
            self.date_frame, 
            text="Time Travel!", 
            command=self.time_travel
        )
        self.time_travel_btn.pack(side=tk.LEFT, padx=20)
        
        # Create a loading label
        self.loading_var = tk.StringVar()
        self.loading_label = ttk.Label(self.date_frame, textvariable=self.loading_var)
        self.loading_label.pack(side=tk.LEFT, padx=10)
        
        # Create a notebook for different categories
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create tabs for each category
        self.create_tab("overview", "Era Overview")
        self.create_tab("movies", "Movies & TV")
        self.create_tab("music", "Music")
        self.create_tab("events", "Events")
        self.create_tab("technology", "Technology")
        self.create_tab("fashion", "Fashion & Style")
        
    def create_tab(self, tab_id, tab_name):
        # Create a frame for the tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=tab_name)
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store the frame reference
        setattr(self, f"{tab_id}_frame", scrollable_frame)
    
    def time_travel(self):
        """Collect data for the selected date and update the UI"""
        # Show loading indicator
        self.loading_var.set("Loading time machine...")
        self.root.update()
        
        try:
            # Get the selected date
            month = list(calendar.month_name).index(self.month_var.get())
            day = int(self.day_var.get())
            year = int(self.year_var.get())
            
            # Validate date
            try:
                selected_date = datetime(year, month, day)
                formatted_date = selected_date.strftime("%B %d, %Y")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please select a valid date.")
                self.loading_var.set("")
                return
            
            # Start data collection in a separate thread
            threading.Thread(target=self.collect_and_display_data, args=(selected_date,)).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.loading_var.set("")
    
    def collect_and_display_data(self, date):
        """Collect data and update UI"""
        try:
            # Determine the decade for theming
            decade = (date.year // 10) * 10
            decade_style = f"{decade}s"
            
            # Apply era-specific theme if available
            if decade_style in self.decade_colors:
                colors = self.decade_colors[decade_style]
                self.root.tk_setPalette(
                    background=colors["bg"],
                    foreground=colors["text"],
                    activeBackground=colors["accent"],
                    activeForeground="#FFFFFF"
                )
            
            # Format date for display
            formatted_date = date.strftime("%B %d, %Y")
            
            # Collect data for each category
            events_data = self.get_historical_events(date)
            movies_data = self.get_movies_and_tv(date)
            music_data = self.get_music(date)
            tech_data = self.get_technology(date)
            fashion_data = self.get_fashion(date)
            
            # Update UI on the main thread
            self.root.after(0, lambda: self.update_overview_tab(date, decade_style, events_data))
            self.root.after(0, lambda: self.update_events_tab(events_data))
            self.root.after(0, lambda: self.update_movies_tab(movies_data))
            self.root.after(0, lambda: self.update_music_tab(music_data))
            self.root.after(0, lambda: self.update_tech_tab(tech_data))
            self.root.after(0, lambda: self.update_fashion_tab(fashion_data))
            
            # Clear loading indicator
            self.root.after(0, lambda: self.loading_var.set(""))
            
            # Update window title
            self.root.after(0, lambda: self.root.title(f"RetroDay - {formatted_date}"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, lambda: self.loading_var.set(""))
        
    def update_overview_tab(self, date, decade_style, events_data):
        """Update the overview tab with general information about the era"""
        # Clear previous content
        for widget in self.overview_frame.winfo_children():
            widget.destroy()
        
        formatted_date = date.strftime("%B %d, %Y")
        decade = (date.year // 10) * 10
        
        # Header
        header_font = font.Font(family="Arial", size=24, weight="bold")
        header = tk.Label(
            self.overview_frame, 
            text=f"Welcome to {formatted_date}!", 
            font=header_font
        )
        header.pack(pady=20)
        
        # Decade description
        decade_descriptions = {
            1950: "The 1950s: Post-war prosperity, suburban growth, rock 'n' roll, and the birth of modern youth culture.",
            1960: "The 1960s: Civil rights movement, space race, Beatlemania, and counterculture revolution.",
            1970: "The 1970s: Disco fever, oil crisis, Watergate, and the rise of personal computing.",
            1980: "The 1980s: Reagan/Thatcher era, MTV, video games, and neon everything.",
            1990: "The 1990s: Internet boom, grunge music, Seinfeld, and the end of the Cold War.",
            2000: "The 2000s: 9/11 aftermath, iPods, reality TV, and the dawn of social media.",
            2010: "The 2010s: Smartphones everywhere, streaming services, social media dominance, and climate activism.",
            2020: "The 2020s: COVID-19 pandemic, remote work revolution, TikTok, and increasing climate concerns."
        }
        
        decade_label = tk.Label(
            self.overview_frame,
            text=decade_descriptions.get(decade, f"The {decade}s"),
            font=("Arial", 12),
            wraplength=800,
            justify="center"
        )
        decade_label.pack(pady=10)
        
        # Key highlight from that day
        if events_data and len(events_data) > 0:
            highlight = random.choice(events_data)
            highlight_frame = ttk.Frame(self.overview_frame, padding=10)
            highlight_frame.pack(pady=20, fill=tk.X, padx=50)
            
            highlight_label = tk.Label(
                highlight_frame,
                text="On This Day:",
                font=("Arial", 14, "bold")
            )
            highlight_label.pack()
            
            highlight_text = tk.Label(
                highlight_frame,
                text=highlight,
                font=("Arial", 12),
                wraplength=700,
                justify="center"
            )
            highlight_text.pack(pady=5)
        
        # Add a decorative element based on the decade
        decade_imgs = {
            1950: "https://example.com/1950s.jpg",
            1960: "https://example.com/1960s.jpg",
            # Add more decade images here
        }
        
        # Note about using the tabs
        note_label = tk.Label(
            self.overview_frame,
            text="Explore the tabs above to discover more about this time period!",
            font=("Arial", 12, "italic"),
            wraplength=800
        )
        note_label.pack(pady=30)
        
    def update_events_tab(self, events_data):
        """Update the events tab with historical events"""
        # Clear previous content
        for widget in self.events_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Label(
            self.events_frame, 
            text="Historical Events", 
            font=("Arial", 18, "bold")
        )
        header.pack(pady=20)
        
        if not events_data:
            no_data = tk.Label(
                self.events_frame,
                text="No historical events found for this date.",
                font=("Arial", 12)
            )
            no_data.pack(pady=10)
            return
        
        # Display events
        for i, event in enumerate(events_data):
            event_frame = ttk.Frame(self.events_frame, padding=10)
            event_frame.pack(pady=5, fill=tk.X, padx=20)
            
            event_text = tk.Label(
                event_frame,
                text=f"• {event}",
                font=("Arial", 12),
                wraplength=800,
                justify="left",
                anchor="w"
            )
            event_text.pack(fill=tk.X)
            
            # Add a separator, except after the last item
            if i < len(events_data) - 1:
                ttk.Separator(self.events_frame, orient='horizontal').pack(fill='x', padx=40, pady=5)
    
    def update_movies_tab(self, movies_data):
        """Update the movies tab with popular films and TV shows"""
        # Clear previous content
        for widget in self.movies_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Label(
            self.movies_frame, 
            text="Popular Movies & TV", 
            font=("Arial", 18, "bold")
        )
        header.pack(pady=20)
        
        if not movies_data:
            no_data = tk.Label(
                self.movies_frame,
                text="No movie or TV data found for this time period.",
                font=("Arial", 12)
            )
            no_data.pack(pady=10)
            return
        
        # Create a grid layout for movies
        movies_container = ttk.Frame(self.movies_frame)
        movies_container.pack(pady=10, fill=tk.BOTH)
        
        row, col = 0, 0
        for movie in movies_data:
            # Create movie card
            movie_frame = ttk.Frame(movies_container, padding=10)
            movie_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Movie title
            title_label = tk.Label(
                movie_frame,
                text=movie.get("title", "Unknown Title"),
                font=("Arial", 12, "bold"),
                wraplength=200
            )
            title_label.pack()
            
            # Movie details
            if "year" in movie or "director" in movie:
                details = []
                if "year" in movie:
                    details.append(f"Year: {movie['year']}")
                if "director" in movie:
                    details.append(f"Director: {movie['director']}")
                
                details_label = tk.Label(
                    movie_frame,
                    text="\n".join(details),
                    font=("Arial", 10),
                    wraplength=200
                )
                details_label.pack(pady=5)
            
            # Movie poster (placeholder)
            if "poster_url" in movie and movie["poster_url"]:
                try:
                    image_path = self.download_image(movie["poster_url"], f"movie_{movie.get('id', 'unknown')}")
                    if image_path:
                        img = Image.open(image_path)
                        img = img.resize((150, 225), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        poster_label = tk.Label(movie_frame, image=photo)
                        poster_label.image = photo  # Keep a reference
                        poster_label.pack(pady=10)
                except Exception:
                    # If image fails, show placeholder text
                    placeholder = tk.Label(movie_frame, text="[Poster unavailable]", height=5)
                    placeholder.pack(pady=10)
            
            # Update grid position
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
    
    def update_music_tab(self, music_data):
        """Update the music tab with popular songs and artists"""
        # Clear previous content
        for widget in self.music_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Label(
            self.music_frame, 
            text="Popular Music", 
            font=("Arial", 18, "bold")
        )
        header.pack(pady=20)
        
        if not music_data:
            no_data = tk.Label(
                self.music_frame,
                text="No music data found for this time period.",
                font=("Arial", 12)
            )
            no_data.pack(pady=10)
            return
        
        # Display top songs
        songs_label = tk.Label(
            self.music_frame,
            text="Top Songs",
            font=("Arial", 14, "bold")
        )
        songs_label.pack(pady=10)
        
        songs_frame = ttk.Frame(self.music_frame)
        songs_frame.pack(pady=10, fill=tk.X, padx=40)
        
        # Create lists for songs and artists
        row = 0
        for song in music_data.get("songs", []):
            song_frame = ttk.Frame(songs_frame, padding=5)
            song_frame.grid(row=row, column=0, sticky="w", pady=2)
            
            song_text = tk.Label(
                song_frame,
                text=f"• {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown Artist')}",
                font=("Arial", 12),
                anchor="w"
            )
            song_text.pack(side=tk.LEFT)
            
            row += 1
        
        # Display top artists
        if "artists" in music_data and music_data["artists"]:
            artists_label = tk.Label(
                self.music_frame,
                text="Popular Artists",
                font=("Arial", 14, "bold")
            )
            artists_label.pack(pady=(20, 10))
            
            artists_frame = ttk.Frame(self.music_frame)
            artists_frame.pack(pady=10, fill=tk.X, padx=40)
            
            row = 0
            for artist in music_data["artists"]:
                artist_frame = ttk.Frame(artists_frame, padding=5)
                artist_frame.grid(row=row, column=0, sticky="w", pady=2)
                
                artist_text = tk.Label(
                    artist_frame,
                    text=f"• {artist}",
                    font=("Arial", 12),
                    anchor="w"
                )
                artist_text.pack(side=tk.LEFT)
                
                row += 1
        
        # Music trivia or fun fact
        if "trivia" in music_data and music_data["trivia"]:
            trivia_frame = ttk.Frame(self.music_frame, padding=10)
            trivia_frame.pack(pady=20, fill=tk.X, padx=40)
            
            trivia_label = tk.Label(
                trivia_frame,
                text="Music Trivia:",
                font=("Arial", 12, "bold")
            )
            trivia_label.pack(anchor="w")
            
            trivia_text = tk.Label(
                trivia_frame,
                text=random.choice(music_data["trivia"]),
                font=("Arial", 11),
                wraplength=800,
                justify="left"
            )
            trivia_text.pack(pady=5, anchor="w")
    
    def update_tech_tab(self, tech_data):
        """Update the technology tab with tech from the era"""
        # Clear previous content
        for widget in self.technology_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Label(
            self.technology_frame, 
            text="Technology of the Era", 
            font=("Arial", 18, "bold")
        )
        header.pack(pady=20)
        
        if not tech_data:
            no_data = tk.Label(
                self.technology_frame,
                text="No technology data found for this time period.",
                font=("Arial", 12)
            )
            no_data.pack(pady=10)
            return
        
        # Display gadgets
        if "gadgets" in tech_data and tech_data["gadgets"]:
            gadgets_label = tk.Label(
                self.technology_frame,
                text="Popular Gadgets",
                font=("Arial", 14, "bold")
            )
            gadgets_label.pack(pady=10)
            
            gadgets_frame = ttk.Frame(self.technology_frame)
            gadgets_frame.pack(pady=10, fill=tk.X, padx=40)
            
            for i, gadget in enumerate(tech_data["gadgets"]):
                gadget_frame = ttk.Frame(gadgets_frame, padding=5)
                gadget_frame.pack(fill=tk.X, pady=5)
                
                gadget_text = tk.Label(
                    gadget_frame,
                    text=f"• {gadget}",
                    font=("Arial", 12),
                    anchor="w",
                    justify="left"
                )
                gadget_text.pack(side=tk.LEFT)
        
        # Display tech milestones
        if "milestones" in tech_data and tech_data["milestones"]:
            milestones_label = tk.Label(
                self.technology_frame,
                text="Tech Milestones",
                font=("Arial", 14, "bold")
            )
            milestones_label.pack(pady=(20, 10))
            
            milestones_frame = ttk.Frame(self.technology_frame)
            milestones_frame.pack(pady=10, fill=tk.X, padx=40)
            
            for milestone in tech_data["milestones"]:
                milestone_frame = ttk.Frame(milestones_frame, padding=5)
                milestone_frame.pack(fill=tk.X, pady=5)
                
                milestone_text = tk.Label(
                    milestone_frame,
                    text=f"• {milestone}",
                    font=("Arial", 12),
                    wraplength=800,
                    justify="left",
                    anchor="w"
                )
                milestone_text.pack(side=tk.LEFT)
        
        # Display internet/computers state
        if "computing" in tech_data:
            computing_frame = ttk.Frame(self.technology_frame, padding=10)
            computing_frame.pack(pady=20, fill=tk.X, padx=40)
            
            computing_label = tk.Label(
                computing_frame,
                text="Computing & Internet:",
                font=("Arial", 12, "bold")
            )
            computing_label.pack(anchor="w")
            
            computing_text = tk.Label(
                computing_frame,
                text=tech_data["computing"],
                font=("Arial", 11),
                wraplength=800,
                justify="left"
            )
            computing_text.pack(pady=5, anchor="w")
    
    def update_fashion_tab(self, fashion_data):
        """Update the fashion tab with styles from the era"""
        # Clear previous content
        for widget in self.fashion_frame.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Label(
            self.fashion_frame, 
            text="Fashion & Style", 
            font=("Arial", 18, "bold")
        )
        header.pack(pady=20)
        
        if not fashion_data:
            no_data = tk.Label(
                self.fashion_frame,
                text="No fashion data found for this time period.",
                font=("Arial", 12)
            )
            no_data.pack(pady=10)
            return
        
        # Display clothing trends
        if "clothing" in fashion_data and fashion_data["clothing"]:
            clothing_label = tk.Label(
                self.fashion_frame,
                text="Clothing Trends",
                font=("Arial", 14, "bold")
            )
            clothing_label.pack(pady=10)
            
            clothing_frame = ttk.Frame(self.fashion_frame)
            clothing_frame.pack(pady=10, fill=tk.X, padx=40)
            
            for trend in fashion_data["clothing"]:
                trend_frame = ttk.Frame(clothing_frame, padding=5)
                trend_frame.pack(fill=tk.X, pady=5)
                
                trend_text = tk.Label(
                    trend_frame,
                    text=f"• {trend}",
                    font=("Arial", 12),
                    wraplength=800,
                    justify="left",
                    anchor="w"
                )
                trend_text.pack(side=tk.LEFT)
        
        # Display hairstyles
        if "hairstyles" in fashion_data and fashion_data["hairstyles"]:
            hair_label = tk.Label(
                self.fashion_frame,
                text="Popular Hairstyles",
                font=("Arial", 14, "bold")
            )
            hair_label.pack(pady=(20, 10))
            
            hair_frame = ttk.Frame(self.fashion_frame)
            hair_frame.pack(pady=10, fill=tk.X, padx=40)
            
            for style in fashion_data["hairstyles"]:
                style_frame = ttk.Frame(hair_frame, padding=5)
                style_frame.pack(fill=tk.X, pady=5)
                
                style_text = tk.Label(
                    style_frame,
                    text=f"• {style}",
                    font=("Arial", 12),
                    wraplength=800,
                    justify="left",
                    anchor="w"
                )
                style_text.pack(side=tk.LEFT)
        
        # Fashion icons
        if "icons" in fashion_data and fashion_data["icons"]:
            icons_label = tk.Label(
                self.fashion_frame,
                text="Fashion Icons",
                font=("Arial", 14, "bold")
            )
            icons_label.pack(pady=(20, 10))
            
            icons_frame = ttk.Frame(self.fashion_frame)
            icons_frame.pack(pady=10, fill=tk.X, padx=40)
            
            for icon in fashion_data["icons"]:
                icon_frame = ttk.Frame(icons_frame, padding=5)
                icon_frame.pack(fill=tk.X, pady=5)
                
                icon_text = tk.Label(
                    icon_frame,
                    text=f"• {icon}",
                    font=("Arial", 12),
                    anchor="w"
                )
                icon_text.pack(side=tk.LEFT)
    
    def get_historical_events(self, date):
        """Get historical events for the given date"""
        try:
            # Format date for Wikipedia query
            month_name = date.strftime("%B")
            day = date.day
            
            # Try to get events from Wikipedia
            wiki_page = f"{month_name}_{day}"
            try:
                page = wikipedia.page(wiki_page)
                content = page.content
                
                # Extract events for the year or decade
                year = date.year
                decade = (year // 10) * 10
                
                events = []
                
                # Extract events for the specific year if available
                year_pattern = re.compile(rf"{year}.*?–\s*(.*?)(?=\n\n|\n\d|\Z)", re.DOTALL)
                year_matches = year_pattern.findall(content)
                
                if year_matches:
                    for match in year_matches:
                        # Split by newline and process each event
                        for event in match.split("\n"):
                            if event.strip():
                                events.append(f"{year}: {event.strip()}")
                
                # If no specific events for the year, look for the decade
                if not events:
                    decade_pattern = re.compile(rf"{decade}s.*?–\s*(.*?)(?=\n\n|\n\d|\Z)", re.DOTALL)
                    decade_matches = decade_pattern.findall(content)
                    
                    if decade_matches:
                        for match in decade_matches:
                            for event in match.split("\n"):
                                if event.strip():
                                    events.append(f"{decade}s: {event.strip()}")
                                # If still no events, look for general "Events" section
                if not events:
                    events_section = re.search(r"== Events ==(.*?)(?==\=|\Z)", content, re.DOTALL)
                    if events_section:
                        events_text = events_section.group(1)
                        # Extract bullet points or specific years
                        event_items = re.findall(r"\*\s*(.*?\d{4}.*?)(?=\n\*|\n\n|\Z)", events_text)
                        events.extend(event_items)
                
                return events[:10]  # Return up to 10 events
            
            except wikipedia.exceptions.PageError:
                # Fallback to scraping on this day in history websites
                try:
                    url = f"https://www.onthisday.com/day/{month_name.lower()}/{day}"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    events = []
                    event_sections = soup.find_all('section', class_='event-list')
                    
                    for section in event_sections:
                        year = section.find('h3').get_text().strip()
                        event_items = section.find_all('li')
                        
                        for item in event_items:
                            event_text = item.get_text().strip()
                            events.append(f"{year}: {event_text}")
                    
                    return events[:10]
                
                except Exception:
                    pass
            
            # Final fallback - return some generic events based on decade
            decade = (date.year // 10) * 10
            decade_events = {
                1950: [
                    "The post-war economic boom leads to suburban expansion",
                    "Rock 'n' roll music emerges as a cultural force",
                    "The Cold War begins between the US and Soviet Union"
                ],
                1960: [
                    "Civil Rights Movement gains momentum",
                    "The Beatles revolutionize popular music",
                    "Humans land on the moon (1969)"
                ],
                # Add more decades as needed
            }
            
            return decade_events.get(decade, ["No specific historical events found for this date."])
        
        except Exception as e:
            print(f"Error getting historical events: {e}")
            return ["Could not retrieve historical events."]
    
    def get_movies_and_tv(self, date):
        """Get popular movies and TV shows from around the given date"""
        try:
            year = date.year
            decade = (year // 10) * 10
            
            # Try to use TMDB API if available
            if self.tmdb_api_key:
                try:
                    # Get popular movies from that year
                    url = f"https://api.themoviedb.org/3/discover/movie?api_key={self.tmdb_api_key}" \
                          f"&primary_release_year={year}&sort_by=popularity.desc"
                    
                    response = requests.get(url)
                    data = response.json()
                    
                    movies = []
                    for movie in data.get('results', [])[:5]:  # Get top 5
                        movie_data = {
                            'title': movie.get('title', 'Unknown'),
                            'year': year,
                            'id': movie.get('id'),
                            'poster_url': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}" if movie.get('poster_path') else None
                        }
                        
                        # Get director info if available
                        credits_url = f"https://api.themoviedb.org/3/movie/{movie['id']}/credits?api_key={self.tmdb_api_key}"
                        credits_response = requests.get(credits_url)
                        credits_data = credits_response.json()
                        
                        for person in credits_data.get('crew', []):
                            if person.get('job') == 'Director':
                                movie_data['director'] = person.get('name')
                                break
                        
                        movies.append(movie_data)
                    
                    return movies
                
                except Exception:
                    pass
            
            # Fallback to decade-based movie data
            decade_movies = {
                1950: [
                    {"title": "Singin' in the Rain", "year": 1952, "director": "Gene Kelly, Stanley Donen"},
                    {"title": "Rear Window", "year": 1954, "director": "Alfred Hitchcock"},
                    {"title": "Some Like It Hot", "year": 1959, "director": "Billy Wilder"}
                ],
                1960: [
                    {"title": "Psycho", "year": 1960, "director": "Alfred Hitchcock"},
                    {"title": "The Sound of Music", "year": 1965, "director": "Robert Wise"},
                    {"title": "2001: A Space Odyssey", "year": 1968, "director": "Stanley Kubrick"}
                ],
                # Add more decades as needed
            }
            
            return decade_movies.get(decade, [
                {"title": "No specific movie data available", "year": year}
            ])
        
        except Exception as e:
            print(f"Error getting movies: {e}")
            return [{"title": "Could not retrieve movie data", "year": date.year}]
    
    def get_music(self, date):
        """Get popular music from around the given date"""
        try:
            year = date.year
            decade = (year // 10) * 10
            
            # Try to use Last.fm or other music API if available
            # (Implementation would depend on having API access)
            
            # Fallback to decade-based music data
            decade_music = {
                1950: {
                    "songs": [
                        {"title": "Hound Dog", "artist": "Elvis Presley"},
                        {"title": "Johnny B. Goode", "artist": "Chuck Berry"},
                        {"title": "What'd I Say", "artist": "Ray Charles"}
                    ],
                    "artists": ["Elvis Presley", "Chuck Berry", "Little Richard", "Frank Sinatra"],
                    "trivia": [
                        "Rock 'n' roll emerged in the mid-1950s, blending rhythm and blues with country music.",
                        "The 45 rpm single became the standard format for hit songs."
                    ]
                },
                1960: {
                    "songs": [
                        {"title": "Hey Jude", "artist": "The Beatles"},
                        {"title": "(I Can't Get No) Satisfaction", "artist": "The Rolling Stones"},
                        {"title": "Respect", "artist": "Aretha Franklin"}
                    ],
                    "artists": ["The Beatles", "The Rolling Stones", "Bob Dylan", "Aretha Franklin"],
                    "trivia": [
                        "The British Invasion, led by The Beatles, changed American music in 1964.",
                        "Woodstock Festival in 1969 became a defining moment for 1960s counterculture."
                    ]
                },
                # Add more decades as needed
            }
            
            return decade_music.get(decade, {
                "songs": [{"title": "No specific song data available", "artist": "Unknown"}],
                "artists": ["No artist data available"],
                "trivia": ["No music trivia available for this period."]
            })
        
        except Exception as e:
            print(f"Error getting music: {e}")
            return {
                "songs": [{"title": "Could not retrieve music data", "artist": "Error"}],
                "artists": ["Error"],
                "trivia": ["Could not retrieve music trivia."]
            }
    
    def get_technology(self, date):
        """Get technology trends from around the given date"""
        try:
            year = date.year
            decade = (year // 10) * 10
            
            decade_tech = {
                1950: {
                    "gadgets": ["Transistor radio", "Black-and-white TV", "Electric typewriter"],
                    "milestones": [
                        "First commercial computer (UNIVAC I) released in 1951",
                        "First transistor radio introduced in 1954",
                        "Sputnik 1, the first artificial satellite, launched in 1957"
                    ],
                    "computing": "Computers were room-sized machines used mainly by governments and large corporations. Programming was done with punch cards."
                },
                1960: {
                    "gadgets": ["Portable cassette player", "Color TV", "Electronic calculator"],
                    "milestones": [
                        "First video game (Spacewar!) created in 1962",
                        "ARPANET, precursor to the internet, developed in 1969",
                        "First human on the moon in 1969"
                    ],
                    "computing": "Mainframe computers became more widespread in businesses. The concept of personal computing was still in its infancy."
                },
                # Add more decades as needed
            }
            
            return decade_tech.get(decade, {
                "gadgets": ["No specific gadget data available"],
                "milestones": ["No specific tech milestones available"],
                "computing": "No computing information available for this period."
            })
        
        except Exception as e:
            print(f"Error getting technology: {e}")
            return {
                "gadgets": ["Could not retrieve gadget data"],
                "milestones": ["Could not retrieve tech milestones"],
                "computing": "Could not retrieve computing information."
            }
    
    def get_fashion(self, date):
        """Get fashion trends from around the given date"""
        try:
            year = date.year
            decade = (year // 10) * 10
            
            decade_fashion = {
                1950: {
                    "clothing": [
                        "Poodle skirts with sweater sets",
                        "Men's suits with narrow ties",
                        "Pedal pushers and saddle shoes"
                    ],
                    "hairstyles": [
                        "Pompadour for men",
                        "Poodle cut for women",
                        "Ducktail hairstyle"
                    ],
                    "icons": ["Marilyn Monroe", "James Dean", "Audrey Hepburn"]
                },
                1960: {
                    "clothing": [
                        "Mini skirts and go-go boots",
                        "Mod suits with skinny ties",
                        "Tie-dye and psychedelic prints"
                    ],
                    "hairstyles": [
                        "Beehive hairdos",
                        "Long, straight hair (hippie style)",
                        "The Beatles mop-top"
                    ],
                    "icons": ["Twiggy", "The Beatles", "Jacqueline Kennedy"]
                },
                # Add more decades as needed
            }
            
            return decade_fashion.get(decade, {
                "clothing": ["No specific clothing data available"],
                "hairstyles": ["No specific hairstyle data available"],
                "icons": ["No fashion icons available for this period"]
            })
        
        except Exception as e:
            print(f"Error getting fashion: {e}")
            return {
                "clothing": ["Could not retrieve clothing data"],
                "hairstyles": ["Could not retrieve hairstyle data"],
                "icons": ["Could not retrieve fashion icons"]
            }
    
    def download_image(self, url, filename):
        """Download and cache an image from a URL"""
        try:
            # Check cache first
            cache_path = os.path.join("cache", f"{filename}.jpg")
            if os.path.exists(cache_path):
                return cache_path
            
            # Download the image
            response = requests.get(url)
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                return cache_path
        
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

def main():
    root = ThemedTk(theme="equilux")  # Using a themed Tkinter window
    app = RetroDay(root)
    root.mainloop()

if __name__ == "__main__":
    main()
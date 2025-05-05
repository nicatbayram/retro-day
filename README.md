# RetroDay - Your Time Capsule

RetroDay is a nostalgic desktop application that lets you travel back in time to explore different eras through popular culture, technology, fashion, and historical events.

<img width="500" alt="pdf1" src="https://github.com/user-attachments/assets/ac950abc-918e-40b3-baac-3b4179fdff05" />

## 🌟 Features

- **Time Travel**: Select any date between 1950 and the present to see what life was like during that era
- **Era Overview**: Get a snapshot of the selected decade's culture and significant events
- **Movies & TV**: Discover popular films and television shows from your chosen time period
- **Music**: Explore hit songs, popular artists, and musical trends
- **Historical Events**: Learn about important events that happened on your selected date
- **Technology**: See what gadgets, computers, and technological innovations defined the era
- **Fashion & Style**: View clothing trends, hairstyles, and fashion icons from the time period
- **Era-Specific Theming**: The app's visual style changes to match each decade's aesthetic

## 📋 Requirements

- Python 3.6 or higher
- Tkinter (usually comes with Python)
- Internet connection (for fetching historical data)

## 🔧 Installation

1. Clone this repository or download the source code
```
git clone https://github.com/nicatbayram/retro-day.git
cd retroday
```

2. Install the required dependencies
   
## 📚 Dependencies

- tkinter - For the GUI components
- ttkthemes - For themed UI elements
- PIL (Pillow) - For image processing
- requests - For API calls
- wikipedia - For historical data
- BeautifulSoup4 - For web scraping

  
3. Run the application
```
python main.py
```

## 🚀 Usage

1. **Select a Date**: Choose a month, day, and year using the dropdown menus
2. **Time Travel**: Click the "Time Travel!" button to explore that time period
3. **Browse Tabs**: Navigate through the different categories to learn about various aspects of the era
4. **Enjoy the Nostalgia**: Immerse yourself in the culture, trends, and events of the past!

## 🔑 API Keys (Optional)

For enhanced functionality with movie and news data, you can obtain API keys from:
- [TMDB API](https://www.themoviedb.org/documentation/api) - For movie data
- [News API](https://newsapi.org/) - For historical news

Create a file named `api_keys.json` in the application directory with the following structure:
```json
{
  "tmdb": "your_tmdb_api_key",
  "news": "your_news_api_key"
}
```

## 🖌️ Customization

You can customize the decade colors by modifying the `decade_colors` dictionary in the `RetroDay` class. Each decade can have its own background, accent, and text colors.

## 💡 How It Works

RetroDay combines data from multiple sources:
- Wikipedia for historical events
- TMDB API for movie information
- Web scraping for additional historical context
- Built-in databases for decade-specific information

The app presents this information in a visually appealing interface with era-appropriate styling.

## 🛠️ Contributing

Contributions are welcome! Here are ways you can contribute:
- Add more detailed data for specific decades
- Improve the UI/UX design
- Add new features or categories
- Fix bugs or optimize performance


Created with ❤️ for nostalgia lovers everywhere. Enjoy your trip through time!

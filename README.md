# Quiz-Card-Creator
# Quiz Card Creator - Anki Addon

An advanced Anki addon that creates quiz cards from existing vocabulary cards with random selection options.

## Features

- **Seamless Integration**: Adds menu items to Anki Browser Edit menu and Tools menu
- **Smart Card Creation**: Creates quiz cards with randomly selected vocabulary
- **Duplicate Prevention**: Automatically skips cards that already have quiz versions
- **Flexible Configuration**: Customizable number of random cards and other options
- **Modern UI**: Clean, responsive interface with scroll support for long content
- **Multi-platform**: Compatible with Windows, macOS, and Linux

## Screenshot

![Quiz Card Creator Interface](screenshot.png)

## Requirements

- **Anki**: Version 25.02.5 or higher
- **Python**: 3.9+
- **Qt**: 6.6.2
- **PyQt**: 6.6.1

## Installation

### Method 1: Direct Installation
1. Download the latest release from the [Releases page](https://github.com/yourusername/QuizCardCreator/releases)
2. Extract the files to your Anki addons folder:
   - **Windows**: `C:\Users\YourUsername\AppData\Roaming\Anki2\addons21\`
   - **macOS**: `~/Library/Application Support/Anki2/addons21/`
   - **Linux**: `~/.local/share/Anki2/addons21/`
3. Restart Anki

### Method 2: Manual Installation
1. Clone or download this repository
2. Copy the `QuizCardCreator` folder to your Anki addons folder
3. Restart Anki

## Usage

### Creating Quiz Cards

1. **Open the Quiz Card Creator**:
   - From Browser: Select cards → Edit → "Create Quiz Card Note..."
   - From Main Window: Tools → "Create Quiz Card Notes..."

2. **Configure Settings**:
   - **Source Deck**: Select the deck containing your vocabulary cards
   - **Source Note Type**: Choose the note type of your vocabulary cards
   - **Vocabulary Field**: Select the field containing the vocabulary word
   - **Meaning Field**: Select the field containing the word's meaning
   - **Target Note Type**: Choose the note type for the new quiz cards
   - **Save to Deck**: Choose where to save the new quiz cards
     - Create new "Quiz Notes" deck (recommended)
     - Select existing deck
   - **Advanced Options**:
     - Skip existing quiz cards (prevents duplicates)
     - Number of random cards (1-10)

3. **Create Cards**:
   - Click "Create Quiz Cards"
   - Monitor progress in the progress bar
   - Review the results summary

### How Quiz Cards Work

The addon creates quiz cards with this structure:

1. **Original Content**: All fields from the source card are copied
2. **Quiz Field**: A new "Quiz" field is added containing:
   - 3 randomly selected vocabulary words from the same deck
   - Format: `[word1][meaning1]|[word2][meaning2]|[word3][meaning3]`
3. **Tag**: All quiz cards are tagged with `quiz_generated`

## Configuration

Edit `config.json` to customize:

```json
{
    "default_quiz_deck_name": "Quiz Notes",
    "quiz_field_name": "Quiz",
    "max_random_cards": 3,
    "skip_existing_cards": true,
    "prevent_duplicates": true
}
```

## Development

### Project Structure

```
QuizCardCreator/
├── __init__.py          # Addon entry point
├── main.py             # Main addon logic and hooks
├── dialog.py           # Main dialog window
├── config.json         # Configuration file
├── manifest.json       # Addon metadata
├── requirements.txt    # Python dependencies
└── icons/              # Icon resources (optional)
```

### Building from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/QuizCardCreator.git
   ```

2. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```

3. Copy to Anki addons folder

### Testing

1. Run Anki in development mode (if available)
2. Test the addon with different note types and deck structures
3. Verify no duplicate cards are created

## Troubleshooting

### Common Issues

1. **Addon not appearing in Anki**:
   - Check that files are in the correct addons folder
   - Restart Anki completely
   - Check Anki's addon manager for errors

2. **"No notes found" error**:
   - Ensure your source deck contains cards
   - Verify the note type selection matches your cards

3. **Duplicate cards created**:
   - Enable "Skip existing quiz cards" option
   - Check that the "Quiz" field name matches in config.json

4. **Performance issues with large decks**:
   - The addon batches processing for better performance
   - Consider processing smaller decks or using filters

### Debug Mode

To enable debug logging, add this to your Anki console or create a debug script.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Use type hints for better code clarity
- Add comments for complex logic
- Update documentation when adding new features
- Test thoroughly with different Anki versions

## Roadmap

### Planned Features
- [ ] Preview generated quiz cards before creation
- [ ] Filter by tags when selecting source cards
- [ ] Custom quiz templates and formats
- [ ] Batch processing across multiple decks
- [ ] Undo/Redo support for created cards
- [ ] Export/Import configuration profiles
- [ ] Statistics and reporting
- [ ] Multi-language interface

### Known Limitations
- Currently only supports basic note types
- Quiz format is fixed (could be made customizable)
- Large decks may take time to process

## Support

### Documentation
- [Anki Add-on Development](https://addon-docs.ankiweb.net/)
- [Anki Python API](https://github.com/ankitects/anki)

### Issues and Questions
- Report bugs: [GitHub Issues](https://github.com/yourusername/QuizCardCreator/issues)
- Ask questions: GitHub Discussions or Anki Forums

### Community
- Join the Anki community on Reddit: r/Anki
- Participate in Anki forums for addon discussions

## License

This project is licensed under the GNU AGPLv3 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Anki](https://apps.ankiweb.net/) - The amazing spaced repetition software
- [Anki Add-on Development Community](https://addon-docs.ankiweb.net/) - For excellent documentation and support
- All contributors and testers who help improve this addon

## Disclaimer

This addon is not officially associated with Anki or Damien Elmes. Use at your own risk. Always back up your Anki collection before using new addons.

---

**Happy Studying!** 📚✨

If you find this addon useful, consider giving it a star on GitHub!

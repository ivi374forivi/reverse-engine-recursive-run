# GitHub Copilot Chat Quick Start Guide

## Getting Started in 5 Minutes

### 1. Prerequisites
- GitHub Copilot subscription (Individual, Business, or Enterprise)
- Supported IDE installed (VS Code, Visual Studio, JetBrains, or Neovim)
- Copilot extension/plugin installed and activated

### 2. Open Copilot Chat
**VS Code:**
- Click the chat icon in the activity bar, or
- Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (Mac), or
- Use Command Palette: `Ctrl+Shift+P` → "GitHub Copilot: Open Chat"

**Visual Studio:**
- Click the Copilot Chat icon in the toolbar, or
- Use View → Copilot Chat

**JetBrains:**
- Click the Copilot icon in the toolbar, or
- Right-click in editor → Copilot → Start Chat

### 3. Your First Questions

#### Example 1: Explain Code
1. Select some code in your editor
2. In Copilot Chat, type: `/explain`
3. Press Enter

#### Example 2: Generate Code
In the chat, type:
```
Generate a function that converts Celsius to Fahrenheit
```

#### Example 3: Fix a Bug
1. Select buggy code
2. Type: `/fix`
3. Review and apply the suggestion

### 4. Essential Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/explain` | Explain selected code | `/explain` |
| `/fix` | Fix problems | `/fix` |
| `/tests` | Generate tests | `/tests` |
| `/doc` | Add documentation | `/doc` |
| `/help` | Get help | `/help` |

### 5. Tips for Better Results

#### ✅ DO:
```
"Write a React component that displays a user profile with avatar, name, and email"
```

#### ❌ DON'T:
```
"make component"
```

#### ✅ DO:
```
"How can I optimize this loop to reduce time complexity from O(n²) to O(n)?"
```

#### ❌ DON'T:
```
"make faster"
```

## Common Use Cases

### Generate a Function
**Prompt:**
```
Create a JavaScript function that validates a phone number in E.164 format
```

### Debug an Error
**Prompt:**
```
Why am I getting "TypeError: Cannot read property 'length' of null" in this function?
[paste your code]
```

### Refactor Code
**Prompt:**
```
Refactor this nested if-else structure to use a switch statement or object lookup
```

### Write Tests
**Prompt:**
```
Generate Jest unit tests for this authentication function
```

### Add Documentation
**Prompt:**
```
Add JSDoc comments to this class
```

## Next Steps

1. **Read the full reference**: Check out [COPILOT_CHAT_REFERENCE.md](./COPILOT_CHAT_REFERENCE.md)
2. **Practice**: Try asking questions about your current project
3. **Experiment**: Test different prompting styles
4. **Learn**: Study the code Copilot generates
5. **Iterate**: Refine your questions based on responses

## Keyboard Shortcuts

### VS Code
- Open Chat: `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (Mac)
- Inline Chat: `Ctrl+I` or `Cmd+I`
- Accept Suggestion: `Tab`
- Dismiss: `Esc`

### Visual Studio
- Open Chat: `Alt+/`
- Inline Chat: `Alt+\`

## Troubleshooting

### Chat Not Working?
1. ✓ Check internet connection
2. ✓ Verify Copilot subscription is active
3. ✓ Ensure extension is enabled
4. ✓ Restart your IDE
5. ✓ Sign out and sign back in to GitHub

### Need Help?
- Use `/help` command in chat
- Visit [GitHub Copilot Docs](https://docs.github.com/copilot)
- Check [GitHub Community](https://github.com/community)

## Pro Tips

1. **Context is King**: The more context you provide, the better the response
2. **Use Slash Commands**: They're optimized for common tasks
3. **Iterate**: Don't expect perfection on first try
4. **Reference Files**: Use `#file:filename` to reference specific files
5. **Review Everything**: Always review and test generated code

---

**Ready to dive deeper?** Check out the [complete reference guide](./COPILOT_CHAT_REFERENCE.md) for advanced features and best practices.

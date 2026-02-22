# Player Setup Guide

Welcome to the Tenelis vault! Follow these steps to get everything set up so you can access session recaps, loot tables, maps, and all the campaign content — and push your own character notes back to the group.

---

## Step 1: Install Git

Download and install **Git for Windows** from [git-scm.com](https://git-scm.com/download/win).

During installation, just **click "Next" through every screen** — the defaults are fine.

After installing, open a terminal (search for **"Git Bash"** or **"Terminal"** in the Start menu) and run these two commands with **your** name and email so Git knows who you are:

```
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 2: Clone the Vault

In the same terminal, navigate to where you want the vault to live (e.g. your Documents folder), then clone it:

```
cd ~/Documents
git clone https://github.com/testingcon10/dnd-stuff.git
```

This creates a `dnd-stuff` folder containing the vault.

## Step 3: Open in Obsidian

1. Open **Obsidian** (download from [obsidian.md](https://obsidian.md) if you don't have it)
2. Click **"Open folder as vault"**
3. Navigate into the cloned `dnd-stuff` folder and select the **`Tenelis`** subfolder
4. When prompted to **"Trust this vault"**, click **Trust** — this enables the community plugins (maps, Git sync, etc.)

## Step 4: You're Done!

The vault is now set up. Every time you open it, the **Obsidian Git** plugin automatically pulls the latest content from the DM.

---

## Pushing Your Changes

When you've edited your character sheet, added notes, or made other changes you want to share:

1. Press `Ctrl+P` to open the **Command Palette**
2. Type **"commit"**
3. Select **"Obsidian Git: Commit all changes and push"**

That's it — your changes are now uploaded for everyone to see.

---

## Troubleshooting

### "Please tell me who you are" / "please set user.name"
You skipped the `git config` step. Open a terminal and run:
```
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Merge conflict (file shows `<<<<<<<` markers)
This happens when two people edit the same lines. Don't panic:
1. Open the file in Obsidian
2. You'll see sections marked with `<<<<<<<`, `=======`, and `>>>>>>>`
3. Keep the text you want, delete the markers and the text you don't want
4. Save the file
5. Use `Ctrl+P` → **"Obsidian Git: Commit all changes and push"** to finish resolving

### "Authentication failed"
GitHub needs you to log in. When prompted, sign in with your GitHub account. If you're using HTTPS, you may need to generate a **Personal Access Token**:
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it a name, select the **repo** scope, and click **Generate**
4. Copy the token and use it as your password when Git asks

### Plugin not loading / "Restricted mode"
1. Go to **Settings** (gear icon) → **Community plugins**
2. Turn off **"Restricted mode"**
3. Make sure **Obsidian Git** is listed and toggled **on**

### Nothing happens when I try to push
Make sure you have an internet connection and that you've been added as a collaborator on the GitHub repository. Ask the DM to add your GitHub username.

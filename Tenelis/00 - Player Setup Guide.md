# Player Setup Guide

Get the Tenelis vault on your computer in 4 steps. Takes about 10 minutes.

---

## Step 1: Install two apps

Install both of these (just click **Next** through both installers, don't change any settings):

- **Git** — [Click here to download](https://git-scm.com/download/win)
- **Obsidian** — [Click here to download](https://obsidian.md)

## Step 2: Download the vault

1. Open the **Start menu**, type **Git Bash**, and open it (a black terminal window appears)
2. Copy and paste this **entire block** into the window, then press **Enter**:

```
cd ~/Documents && git clone https://github.com/testingcon10/dnd-stuff.git
```

3. A GitHub sign-in window will pop up — **sign in with your GitHub account**
4. Wait for it to finish (you'll see the blinking cursor return)
5. Close the window

Your vault is now in your **Documents** folder inside a folder called **dnd-stuff**.

## Step 3: Open the vault in Obsidian

1. Open **Obsidian**
2. Click **Open folder as vault**
3. Go to **Documents → dnd-stuff → Tenelis** and select that folder
4. A popup asks if you trust this vault — click **Trust and enable plugins**

## Step 4: Set your name in Git

This only needs to be done once so Git knows who made changes.

1. Open **Git Bash** again from the Start menu
2. Copy and paste these two lines **one at a time**, replacing the name and email with your own, and press **Enter** after each:

```
git config --global user.name "Your Name"
```

```
git config --global user.email "your.email@example.com"
```

3. Close the window

**You're all set!** Every time you open the vault, it automatically downloads the latest content.

---

## How to save your changes

After editing your character sheet or adding notes:

1. Press **Ctrl+P** (opens a search bar at the top of Obsidian)
2. Type **commit**
3. Click **Obsidian Git: Commit all changes and push**

Your changes are now uploaded for everyone.

---

## Something not working?

**"Please tell me who you are"**
You need to do Step 4 above.

**GitHub sign-in window won't appear / "Authentication failed"**
Open Git Bash and paste this, then press Enter:
```
git clone https://github.com/testingcon10/dnd-stuff.git ~/Desktop/test-clone
```
A sign-in window should appear. Sign in, then delete the **test-clone** folder from your Desktop.

**Weird symbols in a file like `<<<<<<<` and `>>>>>>>`**
Two people edited the same lines. Open the file, keep the text you want, delete everything that looks like `<<<<<<<`, `=======`, and `>>>>>>>`. Then save and push your changes (Ctrl+P → commit).

**Plugins aren't working**
Open Obsidian **Settings** (gear icon at bottom left) → **Community plugins** → turn **off** "Restricted mode" → make sure the plugins are toggled on.

**"I pushed and now nothing works" / something went really wrong**
Don't panic — everything is saved on GitHub. Message the DM and we'll sort it out.

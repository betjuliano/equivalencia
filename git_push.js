const git = require('isomorphic-git');
const http = require('isomorphic-git/http/node');
const fs = require('fs');
const path = require('path');

const dir = process.cwd();
const remoteUrl = 'https://github.com/betjuliano/equivalencia.git';
const token = fs.readFileSync(path.join(dir, '.github_token'), 'utf8').trim();

async function run() {
  console.log('--- Git Push Script ---');
  
  // 1. Initialize
  console.log('Initializing repository...');
  await git.init({ fs, dir });

  // 1.5 Add Remote
  console.log('Adding remote origin...');
  await git.addRemote({
    fs,
    dir,
    remote: 'origin',
    url: remoteUrl
  });

  // 2. Add files
  console.log('Staging files...');
  // We need to recursively find all files excluding ignored ones.
  // For simplicity, we'll use a basic recursive add.
  async function addFiles(currentDir) {
    const files = fs.readdirSync(currentDir);
    for (const file of files) {
      const fullPath = path.join(currentDir, file);
      const relativePath = path.relative(dir, fullPath);
      
      // Basic ignore list (simple version of .gitignore)
      if (['node_modules', '.next', '.git', '__pycache__', '.env', '.github_token', '_evo-output'].includes(file)) continue;
      
      if (fs.statSync(fullPath).isDirectory()) {
        await addFiles(fullPath);
      } else {
        await git.add({ fs, dir, filepath: relativePath });
      }
    }
  }
  await addFiles(dir);

  // 3. Commit
  console.log('Committing...');
  await git.commit({
    fs,
    dir,
    author: {
      name: 'EVO Master',
      email: 'evo-master@example.com'
    },
    message: 'Initial commit from EVO Master'
  });

  // 4. Push
  console.log('Pushing to remote...');
  try {
    const pushResult = await git.push({
      fs,
      http,
      dir,
      remote: 'origin',
      ref: 'main',
      url: remoteUrl,
      onAuth: () => ({ username: token }) // Using token as username for PAT
    });
    console.log('Push completed:', pushResult);
  } catch (err) {
    if (err.message.includes('remote error: branch "main" not found')) {
        // Try pushing to a new branch if remote is empty
        console.log('Retrying push to new branch...');
        await git.push({
            fs,
            http,
            dir,
            force: true,
            remote: 'origin',
            url: remoteUrl,
            onAuth: () => ({ username: token })
        });
    } else {
        throw err;
    }
  }
}

run().catch(err => {
  console.error('Error during git operation:', err);
  process.exit(1);
});

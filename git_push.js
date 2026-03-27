const git = require('isomorphic-git');
const http = require('isomorphic-git/http/node');
const fs = require('fs');
const path = require('path');

const dir = process.cwd();
const remoteUrl = 'https://github.com/betjuliano/equivalencia.git';
const token = fs.readFileSync(path.join(dir, '.github_token'), 'utf8').trim();

async function run() {
  console.log('--- Comprehensive Git Push Script ---');
  
  // 1. Initialize (already initialized, but init is idempotent)
  console.log('Verifying repository...');
  await git.init({ fs, dir });

  // 1.5 Add/Verify Remote
  console.log('Verifying remote origin...');
  try {
      await git.addRemote({ fs, dir, remote: 'origin', url: remoteUrl });
  } catch (e) {
      // Ignorato se già presente
  }

  // 2. Add files
  console.log('Staging files (including EVO configs)...');
  async function addFiles(currentDir) {
    const files = fs.readdirSync(currentDir);
    for (const file of files) {
      const fullPath = path.join(currentDir, file);
      const relativePath = path.relative(dir, fullPath);
      
      // Strict ignore list for security and size
      if ([
        'node_modules', '.next', '.git', '__pycache__', '.env', '.github_token', 
        '_evo-output', '.gemini', '.claude', '.opencode', 'brain', 'tmp'
      ].includes(file)) continue;
      
      // Wait, if I want to include .agents and .agent, I SHOULD NOT continue.
      // But the list above includes '.agent'. Let me fix it.
      
      if (fs.statSync(fullPath).isDirectory()) {
        await addFiles(fullPath);
      } else {
        await git.add({ fs, dir, filepath: relativePath });
      }
    }
  }
  
  // Actually, I'll use git.add with a custom glob pattern or just walk carefully.
  // Including .agents and .agent
  await addFiles(dir);

  // 3. Commit
  console.log('Committing updates...');
  try {
    const commitId = await git.commit({
        fs,
        dir,
        author: { name: 'EVO Master', email: 'evo-master@example.com' },
        message: 'Comprehensive project synchronization from EVO Master'
    });
    console.log('Commit ID:', commitId);
  } catch (err) {
      if (err.code === 'NothingToCommitError') {
          console.log('Nothing new to commit.');
      } else {
          throw err;
      }
  }

  // 4. Push
  console.log('Pushing everything to remote...');
  const pushResult = await git.push({
    fs,
    http,
    dir,
    remote: 'origin',
    ref: 'main',
    url: remoteUrl,
    force: true,
    onAuth: () => ({ username: token })
  });
  console.log('Push results:', JSON.stringify(pushResult, null, 2));
}

run().catch(err => {
  console.error('CRITICAL ERROR:', err);
  process.exit(1);
});

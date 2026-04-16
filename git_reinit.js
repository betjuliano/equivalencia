const git = require('isomorphic-git');
const http = require('isomorphic-git/http/node');
const fs = require('fs');
const path = require('path');

const dir = process.cwd();
const remoteUrl = 'https://github.com/betjuliano/equivalencia.git';
// Token should be provided via environment variable GITHUB_TOKEN
const token = process.env.GITHUB_TOKEN || '';

async function run() {
  console.log('--- Clean Git Re-initialization & Push ---');
  
  // 1. Init
  console.log('Initializing new repository...');
  await git.init({ fs, dir });

  // 2. Config Identity
  console.log('Configuring local identity...');
  await git.setConfig({ fs, dir, path: 'user.name', value: 'Pccli' });
  await git.setConfig({ fs, dir, path: 'user.email', value: 'pccli@example.com' });
  await git.setConfig({ fs, dir, path: 'core.autocrlf', value: 'true' }); // Normalize line endings on Windows

  // 3. Add Remote
  console.log('Adding remote origin...');
  await git.addRemote({ fs, dir, remote: 'origin', url: remoteUrl });

  // 4. Staging with Path Normalization
  console.log('Staging files with normalization...');
  async function stageRecursively(currentPath) {
    const files = fs.readdirSync(currentPath);
    for (const file of files) {
      const fullPath = path.join(currentPath, file);
      const relativePath = path.relative(dir, fullPath);
      
      // Normalized path for Git (must use forward slashes)
      const normalizedPath = relativePath.split(path.sep).join('/');

      // Ignore patterns
      if ([
        'node_modules', '.next', '.git', '__pycache__', '.env', '.github_token', 
        '_evo-output', '.gemini', '.claude', '.opencode', 'brain', 'tmp'
      ].includes(file)) continue;

      if (fs.statSync(fullPath).isDirectory()) {
        await stageRecursively(fullPath);
      } else {
        await git.add({ fs, dir, filepath: normalizedPath });
      }
    }
  }
  await stageRecursively(dir);

  // 5. Commit
  console.log('Committing clean state...');
  const commitId = await git.commit({
    fs,
    dir,
    author: { name: 'Pccli', email: 'pccli@example.com' },
    message: 'Clean re-initialization: Fixed duplicateEntries corruption'
  });
  console.log('New Commit ID:', commitId);

  // 5.5 Ensure branch is sync-fix
  const currentBranch = await git.currentBranch({ fs, dir });
  console.log('Current branch is:', currentBranch);
  const headHash = await git.resolveRef({ fs, dir, ref: 'HEAD' });
  
  console.log('Setting sync-fix ref to:', headHash);
  await git.writeRef({
      fs,
      dir,
      ref: 'refs/heads/sync-fix',
      value: headHash,
      force: true
  });

  // 6. Push
  console.log('Pushing everything to a new branch sync-fix...');
  const pushResult = await git.push({
    fs,
    http,
    dir,
    remote: 'origin',
    ref: 'sync-fix',
    url: remoteUrl,
    force: true,
    onAuth: () => ({ username: token })
  });
  console.log('Push Result:', JSON.stringify(pushResult, null, 2));
}

run().catch(console.error);

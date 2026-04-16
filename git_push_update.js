const git = require('isomorphic-git');
const http = require('isomorphic-git/http/node');
const fs = require('fs');
const path = require('path');

const dir = process.cwd();
const remoteUrl = 'https://github.com/betjuliano/equivalencia.git';
const token = process.env.GITHUB_TOKEN || '';

const IGNORE_LIST = [
  'node_modules', '.next', '.git', '__pycache__', '.env', '.github_token',
  '_evo-output', '.gemini', '.claude', '.opencode', 'brain', 'tmp',
  'deploy.tar'
];

async function stageRecursively(currentPath) {
  const files = fs.readdirSync(currentPath);
  for (const file of files) {
    if (IGNORE_LIST.includes(file)) continue;
    const fullPath = path.join(currentPath, file);
    const relativePath = path.relative(dir, fullPath).split(path.sep).join('/');
    if (fs.statSync(fullPath).isDirectory()) {
      await stageRecursively(fullPath);
    } else {
      await git.add({ fs, dir, filepath: relativePath });
    }
  }
}

async function run() {
  console.log('--- Git Update & Push to master ---');

  // Config identity
  await git.setConfig({ fs, dir, path: 'user.name', value: 'Pccli' });
  await git.setConfig({ fs, dir, path: 'user.email', value: 'pccli@example.com' });

  // Stage all
  console.log('Staging all changes...');
  await stageRecursively(dir);

  // Commit
  console.log('Committing...');
  try {
    const commitId = await git.commit({
      fs,
      dir,
      author: { name: 'Pccli', email: 'pccli@example.com' },
      message: 'feat: update project for VPS deployment - Docker config, frontend/backend updates'
    });
    console.log('Commit ID:', commitId);
  } catch (err) {
    if (err.code === 'NothingToCommitError') {
      console.log('Nothing new to commit - already up to date.');
    } else {
      throw err;
    }
  }

  // Push to master
  console.log('Pushing to origin master...');
  const pushResult = await git.push({
    fs,
    http,
    dir,
    remote: 'origin',
    ref: 'master',
    url: remoteUrl,
    force: false,
    onAuth: () => ({ username: token }),
    onMessage: (msg) => console.log('[remote]', msg)
  });
  console.log('Push result:', JSON.stringify(pushResult, null, 2));
  console.log('--- Done! GitHub is up to date. ---');
}

run().catch(err => {
  console.error('ERROR:', err.message || err);
  process.exit(1);
});

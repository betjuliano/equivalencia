const git = require('isomorphic-git');
const fs = require('fs');
const path = require('path');

const dir = process.cwd();

async function run() {
  console.log('--- Git Sync Script ---');
  
  // 1. Initialize/Verify
  await git.init({ fs, dir });

  // 2. Add ALL files to index
  console.log('Staging all files to normalize index...');
  async function addFiles(currentDir) {
    const files = fs.readdirSync(currentDir);
    for (const file of files) {
      const fullPath = path.join(currentDir, file);
      const relativePath = path.relative(dir, fullPath);
      
      if ([
        'node_modules', '.next', '.git', '__pycache__', '.env', '.github_token', 
        '_evo-output', '.gemini', '.claude', '.opencode', 'brain', 'tmp'
      ].includes(file)) continue;
      
      if (fs.statSync(fullPath).isDirectory()) {
        await addFiles(fullPath);
      } else {
        await git.add({ fs, dir, filepath: relativePath });
      }
    }
  }
  await addFiles(dir);

  // 3. Commit the synchronization
  console.log('Committing synchronization...');
  try {
    const commitId = await git.commit({
        fs,
        dir,
        author: { name: 'EVO Master', email: 'evo-master@example.com' },
        message: 'Git Index Synchronization and Line Ending Normalization'
    });
    console.log('Sync Commit ID:', commitId);
  } catch (err) {
      if (err.code === 'NothingToCommitError') {
          console.log('Index is already synchronized.');
      } else {
          throw err;
      }
  }

  // 4. Verify status
  console.log('Verifying status...');
  const status = await git.statusMatrix({ fs, dir });
  const modified = status.filter(row => row[2] !== row[3]);
  console.log('Remaining Modified Files:', modified.length);
}

run().catch(console.error);

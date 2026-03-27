const git = require('isomorphic-git');
const fs = require('fs');
const path = require('path');

const dir = process.cwd();

async function run() {
  console.log('--- Git Diagnostic ---');
  
  // 1. Current Branch
  const branch = await git.currentBranch({ fs, dir });
  console.log('Current Branch:', branch);

  // 2. Status
  console.log('Checking status...');
  const status = await git.statusMatrix({ fs, dir });
  // statusMatrix returns [filepath, head, index, workingTree]
  // 1 = unchanged, 2 = modified/new
  const modified = status.filter(row => row[2] !== row[3]);
  console.log('Modified Files:', modified.length);
  if (modified.length > 0) {
      console.log('Example Modified:', modified.slice(0, 5).map(row => row[0]));
  }
}

run().catch(console.error);

const git = require('isomorphic-git');
const fs = require('fs');
const path = require('path');

const dir = process.cwd();

async function run() {
  console.log('--- Git Config Script ---');
  
  console.log('Setting local user.name...');
  await git.setConfig({
    fs,
    dir,
    path: 'user.name',
    value: 'Pccli'
  });

  console.log('Setting local user.email...');
  await git.setConfig({
    fs,
    dir,
    path: 'user.email',
    value: 'pccli@example.com'
  });

  console.log('Configuration complete.');
}

run().catch(console.error);

/** @type {import('@commitlint/types').UserConfig} */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'body-leading-blank': [2, 'always'],
    'footer-leading-blank': [1, 'always'],
    'header-max-length': [2, 'always', 100],
    'scope-case': [2, 'always', 'lower-case'],
    'subject-case': [2, 'never', ['sentence-case', 'start-case', 'pascal-case', 'upper-case']],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'type-case': [2, 'always', 'lower-case'],
    'type-empty': [2, 'never'],
    'type-enum': [
      2,
      'always',
      [
        'feat', // New feature
        'fix', // Bug fix
        'perf', // Performance improvement
        'refactor', // Code refactoring
        'style', // Formatting, missing semicolons, etc.
        'test', // Adding or updating tests
        'build', // Build system or dependencies
        'ci', // CI configuration
        'chore', // Maintenance tasks
        'docs', // Documentation only changes
        'revert', // Reverting changes
      ],
    ],
  },
  prompt: {
    questions: {
      type: {
        description: 'Select the type of change',
        enum: {
          feat: { description: 'A new feature', title: 'Features' },
          fix: { description: 'A bug fix', title: 'Bug Fixes' },
          perf: { description: 'A code change that improves performance', title: 'Performance' },
          refactor: {
            description: 'A code change that neither fixes a bug nor adds a feature',
            title: 'Code Refactoring',
          },
          style: { description: 'Code formatting, missing semicolons, etc.', title: 'Styles' },
          test: { description: 'Adding or updating tests', title: 'Tests' },
          build: { description: 'Build system or dependencies', title: 'Builds' },
          ci: { description: 'CI configuration', title: 'CI' },
          chore: {
            description: "Other changes that don't modify src or test files",
            title: 'Chores',
          },
          docs: { description: 'Documentation only changes', title: 'Documentation' },
          revert: { description: 'Reverts a previous commit', title: 'Reverts' },
        },
      },
      scope: {
        description: 'What is the scope of this change? (e.g. php, js, python, go, rust)',
      },
      subject: {
        description: 'Write a short, imperative tense description of the change',
      },
      body: {
        description: 'Provide a longer description of the change',
      },
      isBreaking: {
        description: 'Are there any breaking changes?',
      },
      breakingBody: {
        description:
          'A BREAKING CHANGE commit requires a body. Please enter the longer description of the commit itself',
      },
      breaking: {
        description: 'Describe the breaking changes',
      },
      isIssueAffected: {
        description: 'Does this change affect any open issues?',
      },
      issuesBody: {
        description:
          'If issues are closed, the commit requires a body. Please enter the longer description of the commit itself',
      },
      issues: {
        description: 'Add issue references (e.g. "fix #123", "re #123")',
      },
    },
  },
};

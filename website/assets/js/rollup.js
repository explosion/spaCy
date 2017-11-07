/**
 * This file is bundled by Rollup, compiled with Babel and included as
 * <script nomodule> for older browsers that don't yet support JavaScript
 * modules. Browsers that do will ignore this bundle and won't even fetch it
 * from the server. Details:
 * https://github.com/rollup/rollup
 * https://medium.com/dev-channel/es6-modules-in-chrome-canary-m60-ba588dfb8ab7
 */

// Import all modules that are instantiated directly in _includes/_scripts.jade
import ProgressBar from './progress.js';
import NavHighlighter from './nav-highlighter.js';
import Changelog from './changelog.js';
import GitHubEmbed from './github-embed.js';
import Accordion from './accordion.js';
import { ModelLoader, ModelComparer } from './models.js';

// Assign to window so they are bundled by rollup
window.ProgressBar = ProgressBar;
window.NavHighlighter = NavHighlighter;
window.Changelog = Changelog;
window.GitHubEmbed = GitHubEmbed;
window.Accordion = Accordion;
window.ModelLoader = ModelLoader;
window.ModelComparer = ModelComparer;

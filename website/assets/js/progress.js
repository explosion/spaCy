'use strict';

import { $ } from './util.js';

export default class ProgressBar {
    /**
     * Animated reading progress bar.
     * @param {string} selector – CSS selector of progress bar element.
     */
    constructor(selector) {
        this.scrollY = 0;
        this.sizes = this.updateSizes();
        this.el = $(selector);
        this.el.setAttribute('max', 100);
        window.addEventListener('scroll', this.onScroll.bind(this));
        window.addEventListener('resize', this.onResize.bind(this));
    }

    onScroll(ev) {
        this.scrollY = (window.pageYOffset || document.scrollTop) - (document.clientTop || 0);
        requestAnimationFrame(this.update.bind(this));
    }

    onResize(ev) {
        this.sizes = this.updateSizes();
        requestAnimationFrame(this.update.bind(this));
    }

    update() {
        const offset = 100 - ((this.sizes.height - this.scrollY - this.sizes.vh) / this.sizes.height * 100);
        this.el.setAttribute('value', (this.scrollY == 0) ? 0 : offset || 0);
    }

    /**
     * Update scroll and viewport height. Called on load and window resize.
     */
    updateSizes() {
        return {
            height: Math.max(
                document.body.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.clientHeight,
                document.documentElement.scrollHeight,
                document.documentElement.offsetHeight
            ),
            vh: Math.max(
                document.documentElement.clientHeight,
                window.innerHeight || 0
            )
        }
    }
}

import React, { Fragment } from 'react'
import siteMetadata from '../../meta/site.json'
import { domain } from '../../meta/dynamicMeta.mjs'

const isNightly = siteMetadata.nightlyBranches.includes(domain)
export const DEFAULT_BRANCH = isNightly ? 'develop' : 'master'
export const repo = siteMetadata.repo
export const modelsRepo = siteMetadata.modelsRepo
export const projectsRepo = siteMetadata.projectsRepo

/**
 * This is used to provide selectors for headings so they can be crawled by
 * Algolia's DocSearch
 */
export const headingTextClassName = 'heading-text'

/**
 * Create a link to the spaCy repository on GitHub
 * @param {string} filepath - The file path relative to the root of the repo.
 * @param {string} [branch] - Optional branch. Defaults to master.
 * @returns {string} - URL to the file on GitHub.
 */
export function github(filepath, branch = DEFAULT_BRANCH) {
    if (filepath && filepath.startsWith('github.com')) return `https://${filepath}`
    const path = filepath ? '/tree/' + (branch || 'master') + '/' + filepath : ''
    return `https://github.com/${repo}${path}`
}

/**
 * Get the source of a file in the documentation based on its slug
 * @param {string} slug - The slug, e.g. /api/doc.
 * @param {boolean} [isIndex] - Whether the page is an index, e.g. /api/index.mdx
 * @param {string} [branch] - Optional branch on GitHub. Defaults to master.
 */
export function getCurrentSource(slug, isIndex = false, branch = DEFAULT_BRANCH) {
    const ext = isIndex ? '/index.mdx' : '.mdx'
    return github(`website/docs${slug}${ext}`, branch)
}

/**
 * @param obj – The object to check.
 * @returns {boolean} - Whether the object is a string.
 */
export function isString(obj) {
    return typeof obj === 'string' || obj instanceof String
}

/**
 * @param obj - The object to check.
 * @returns {boolean} – Whether the object is an image
 */
export function isImage(obj) {
    if (!obj || !React.isValidElement(obj)) {
        return false
    }
    return obj.props.name == 'img' || obj.props.className == 'gatsby-resp-image-wrapper'
}

/**
 * @param obj - The object to check.
 * @returns {boolean} - Whether the object is empty.
 */
export function isEmptyObj(obj) {
    return Object.entries(obj).length === 0 && obj.constructor === Object
}

/**
 * Join an array of nodes with a given string delimiter, like Array.join for React
 * @param {Array} arr - The elements to join.
 * @param {string} delimiter - String placed between elements.
 * @returns {Node} - The joined array.
 */
export function join(arr, delimiter = ', ') {
    return arr.map((obj, i) => (
        <Fragment key={i}>
            {obj}
            {i < arr.length - 1 && delimiter}
        </Fragment>
    ))
}

/**
 * Convert an array of objects to an object, using a key with a unique value (ID).
 * e.g. [{id: 'foo', bar: 'baz'}] => {foo: { id: 'foo', bar: 'baz'}}
 * @param {Array} arr - The array to convert.
 * @param {string} key - The key value to use to key the dictionary by.
 * @return {Object} - The converted object.
 */
export function arrayToObj(arr, key) {
    return Object.assign({}, ...arr.map((item) => ({ [item[key]]: item })))
}

/**
 * Abbreviate a number, e.g. 14249930 --> 14.25m.
 * @param {number|string} num - The number to convert.
 * @param {number} fixed - Number of decimals.
 * @returns {string} - The abbreviated number.
 */
export function abbrNum(num = 0, fixed = 1) {
    const suffixes = ['', 'k', 'm', 'b', 't']
    if (num === null || num === 0) return 0
    const b = num.toPrecision(2).split('e')
    const k = b.length === 1 ? 0 : Math.floor(Math.min(b[1].slice(1), 14) / 3)
    const n = k < 1 ? num : num / Math.pow(10, k * 3)
    const c = k >= 1 && n >= 100 ? Math.round(n) : n.toFixed(fixed)
    return (c < 0 ? c : Math.abs(c)) + suffixes[k]
}

/**
 * Divide an array into chunks
 * @param {Array} arr - The array to divide.
 * @param {number} chunkSize - Size of the individual chunks.
 * @returns {Array} - The divided array.
 */
export function chunkArray(arr, chunkSize) {
    const base = [...arr]
    const result = []
    while (base.length) {
        result.push(base.splice(0, chunkSize))
    }
    return result
}

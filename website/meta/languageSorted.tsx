import models from './languages.json'

export const languagesSorted = models.languages
    .filter(({ models }) => models && models.length)
    .sort((a, b) => a.name.localeCompare(b.name))

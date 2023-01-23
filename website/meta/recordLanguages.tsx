import models from './languages.json'

const recordLanguages = Object.fromEntries(
    models.languages.map((language, index) => [language.code, language])
)

export default recordLanguages

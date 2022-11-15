import models from './languages.json'

const recordLanguages = Object.fromEntries(
    models.languages.map((language, index) => [
        language.code,
        {
            ...language,
            next: index < models.languages.length - 1 ? models.languages[index + 1] : null,
        },
    ])
)

export default recordLanguages

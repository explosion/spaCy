import React from 'react'
import PropTypes from 'prop-types'
import { StaticQuery, graphql } from 'gatsby'

import {
    LandingHeader,
    LandingTitle,
    LandingSubtitle,
    LandingGrid,
    LandingCard,
    LandingCol,
    LandingButton,
    LandingDemo,
    LandingBannerGrid,
    LandingBanner,
    LandingLogos,
} from '../components/landing'
import { H2 } from '../components/typography'
import { Ul, Li } from '../components/list'
import Button from '../components/button'
import Link from '../components/link'
import irlBackground from '../images/spacy-irl.jpg'

import BenchmarksChoi from 'usage/_benchmarks-choi.md'

const CODE_EXAMPLE = `# pip install spacy
# python -m spacy download en_core_web_sm

import spacy

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")

# Process whole documents
text = ("When Sebastian Thrun started working on self-driving cars at "
        "Google in 2007, few people outside of the company took him "
        "seriously. “I can tell you very senior CEOs of major American "
        "car companies would shake my hand and turn away because I wasn’t "
        "worth talking to,” said Thrun, in an interview with Recode earlier "
        "this week.")
doc = nlp(text)

# Analyze syntax
print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

# Find named entities, phrases and concepts
for entity in doc.ents:
    print(entity.text, entity.label_)
`

/**
 * Compute the overall total counts of models and languages
 */
function getCounts(langs = []) {
    return {
        langs: langs.length,
        modelLangs: langs.filter(({ models }) => models && !!models.length).length,
        models: langs.map(({ models }) => (models ? models.length : 0)).reduce((a, b) => a + b, 0),
    }
}

const Landing = ({ data }) => {
    const counts = getCounts(data.languages)
    return (
        <>
            <LandingHeader>
                <LandingTitle>
                    Industrial-Strength
                    <br />
                    Natural Language
                    <br />
                    Processing
                </LandingTitle>
                <LandingSubtitle>in Python</LandingSubtitle>
            </LandingHeader>
            <LandingGrid blocks>
                <LandingCard title="Get things done">
                    <p>
                        spaCy is designed to help you do real work — to build real products, or
                        gather real insights. The library respects your time, and tries to avoid
                        wasting it. It's easy to install, and its API is simple and productive. We
                        like to think of spaCy as the Ruby on Rails of Natural Language Processing.
                    </p>
                    <LandingButton to="/usage/spacy-101">Get started</LandingButton>
                </LandingCard>
                <LandingCard title="Blazing fast">
                    <p>
                        spaCy excels at large-scale information extraction tasks. It's written from
                        the ground up in carefully memory-managed Cython. Independent research in
                        2015 found spaCy to be the fastest in the world. If your application needs
                        to process entire web dumps, spaCy is the library you want to be using.
                    </p>
                    <LandingButton to="/usage/facts-figures">Facts & Figures</LandingButton>
                </LandingCard>

                <LandingCard title="Deep learning">
                    <p>
                        spaCy is the best way to prepare text for deep learning. It interoperates
                        seamlessly with TensorFlow, PyTorch, scikit-learn, Gensim and the rest of
                        Python's awesome AI ecosystem. With spaCy, you can easily construct
                        linguistically sophisticated statistical models for a variety of NLP
                        problems.
                    </p>
                    <LandingButton to="/usage/training">Read more</LandingButton>
                </LandingCard>
            </LandingGrid>

            <LandingGrid>
                <LandingDemo title="Edit the code & try spaCy">{CODE_EXAMPLE}</LandingDemo>

                <LandingCol>
                    <H2>Features</H2>
                    <Ul>
                        <Li>
                            Non-destructive <strong>tokenization</strong>
                        </Li>
                        <Li>
                            <strong>Named entity</strong> recognition
                        </Li>
                        <Li>
                            Support for <strong>{counts.langs}+ languages</strong>
                        </Li>
                        <Li>
                            <strong>{counts.models} statistical models</strong> for{' '}
                            {counts.modelLangs} languages
                        </Li>
                        <Li>
                            Pre-trained <strong>word vectors</strong>
                        </Li>
                        <Li>State-of-the-art speed</Li>
                        <Li>
                            Easy <strong>deep learning</strong> integration
                        </Li>
                        <Li>Part-of-speech tagging</Li>
                        <Li>Labelled dependency parsing</Li>
                        <Li>Syntax-driven sentence segmentation</Li>
                        <Li>
                            Built in <strong>visualizers</strong> for syntax and NER
                        </Li>
                        <Li>Convenient string-to-hash mapping</Li>
                        <Li>Export to numpy data arrays</Li>
                        <Li>Efficient binary serialization</Li>
                        <Li>
                            Easy <strong>model packaging</strong> and deployment
                        </Li>
                        <Li>Robust, rigorously evaluated accuracy</Li>
                    </Ul>
                </LandingCol>
            </LandingGrid>

            <LandingBannerGrid>
                <LandingBanner
                    title="spaCy IRL 2019: Two days of NLP"
                    label="Join us in Berlin"
                    to="https://irl.spacy.io/2019"
                    button="Get tickets"
                    background="#ffc194"
                    backgroundImage={irlBackground}
                    color="#1a1e23"
                    small
                >
                    We're pleased to invite the spaCy community and other folks working on Natural
                    Language Processing to Berlin this summer for a small and intimate event{' '}
                    <strong>July 5-6, 2019</strong>. The event includes a hands-on training day for
                    teams using spaCy in production, followed by a one-track conference. We've
                    booked a beautiful venue, hand-picked an awesome lineup of speakers and
                    scheduled plenty of social time to get to know each other and exchange ideas.
                </LandingBanner>

                <LandingBanner
                    title="Prodigy: Radically efficient machine teaching"
                    label="From the makers of spaCy"
                    to="https://prodi.gy"
                    button="Try it out"
                    background="#eee"
                    color="#252a33"
                    small
                >
                    Prodigy is an <strong>annotation tool</strong> so efficient that data scientists
                    can do the annotation themselves, enabling a new level of rapid iteration.
                    Whether you're working on entity recognition, intent detection or image
                    classification, Prodigy can help you <strong>train and evaluate</strong> your
                    models faster. Stream in your own examples or real-world data from live APIs,
                    update your model in real-time and chain models together to build more complex
                    systems.
                </LandingBanner>
            </LandingBannerGrid>

            <LandingLogos title="spaCy is trusted by" logos={data.logosUsers}>
                <Button to={`https://github.com/${data.repo}/stargazers`}>and many more</Button>
            </LandingLogos>
            <LandingLogos title="Featured on" logos={data.logosPublications} />

            <LandingBanner
                title="BERT-style language model pretraining"
                label="New in v2.1"
                to="/usage/v2-1"
                button="Read more"
            >
                Learn more from small training corpora by initializing your models with{' '}
                <strong>knowledge from raw text</strong>. The new pretrain command teaches spaCy's
                CNN model to predict words based on their context, producing representations of
                words in contexts. If you've seen Google's BERT system or fast.ai's ULMFiT, spaCy's
                pretraining is similar – but much more efficient. It's still experimental, but users
                are already reporting good results, so give it a try!
            </LandingBanner>

            <LandingGrid cols={2}>
                <LandingCol>
                    <H2>Benchmarks</H2>
                    <p>
                        In 2015, independent researchers from Emory University and Yahoo! Labs
                        showed that spaCy offered the{' '}
                        <strong>fastest syntactic parser in the world</strong> and that its accuracy
                        was <strong>within 1% of the best</strong> available (
                        <Link to="https://aclweb.org/anthology/P/P15/P15-1038.pdf">
                            Choi et al., 2015
                        </Link>
                        ). spaCy v2.0, released in 2017, is more accurate than any of the systems
                        Choi et al. evaluated.
                    </p>
                    <p>
                        <Button to="/usage/facts-figures#benchmarks" large>
                            See details
                        </Button>
                    </p>
                </LandingCol>

                <LandingCol>
                    <BenchmarksChoi />
                </LandingCol>
            </LandingGrid>
        </>
    )
}

Landing.propTypes = {
    data: PropTypes.shape({
        repo: PropTypes.string,
        languages: PropTypes.arrayOf(
            PropTypes.shape({
                models: PropTypes.arrayOf(PropTypes.string),
            })
        ),
        logosUsers: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.string.isRequired,
                url: PropTypes.string.isRequired,
            })
        ),
        logosPublications: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.string.isRequired,
                url: PropTypes.string.isRequired,
            })
        ),
    }),
}

export default () => (
    <StaticQuery query={landingQuery} render={({ site }) => <Landing data={site.siteMetadata} />} />
)

const landingQuery = graphql`
    query LandingQuery {
        site {
            siteMetadata {
                repo
                languages {
                    models
                }
                logosUsers {
                    id
                    url
                }
                logosPublications {
                    id
                    url
                }
            }
        }
    }
`

import React from 'react'
import PropTypes from 'prop-types'

import {
    LandingHeader,
    LandingTitle,
    LandingSubtitle,
    LandingGrid,
    LandingCard,
    LandingCol,
    LandingDemo,
    LandingBannerGrid,
    LandingBanner,
} from '../src/components/landing'
import { H2 } from '../src/components/typography'
import { InlineCode } from '../src/components/inlineCode'
import { Ul, Li } from '../src/components/list'
import Button from '../src/components/button'
import Link from '../src/components/link'

import QuickstartTraining from '../src/widgets/quickstart-training'
import Project from '../src/widgets/project'
import Features from '../src/widgets/features'
import Layout from '../src/templates'
import courseImage from '../public/images/course.jpg'
import prodigyImage from '../public/images/prodigy_overview.jpg'
import projectsImage from '../public/images/projects.png'
import tailoredPipelinesImage from '../public/images/spacy-tailored-pipelines_wide.png'
import { nightly, legacy } from '../meta/dynamicMeta.mjs'

import Benchmarks from '../docs/usage/_benchmarks-models.mdx'
import { ImageFill } from '../src/components/embed'

function getCodeExample(nightly) {
    return `# pip install -U ${nightly ? 'spacy-nightly --pre' : 'spacy'}
# python -m spacy download en_core_web_sm
import spacy

# Load English tokenizer, tagger, parser and NER
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
}

const Landing = () => {
    const codeExample = getCodeExample(nightly)
    return (
        <Layout>
            <LandingHeader nightly={nightly} legacy={legacy}>
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
                <LandingCard title="Get things done" url="/usage/spacy-101" button="Get started">
                    spaCy is designed to help you do real work — to build real products, or gather
                    real insights. The library respects your time, and tries to avoid wasting it.
                    It&apos;s easy to install, and its API is simple and productive.
                </LandingCard>
                <LandingCard
                    title="Blazing fast"
                    url="/usage/facts-figures"
                    button="Facts &amp; Figures"
                >
                    spaCy excels at large-scale information extraction tasks. It&apos;s written from
                    the ground up in carefully memory-managed Cython. If your application needs to
                    process entire web dumps, spaCy is the library you want to be using.
                </LandingCard>

                <LandingCard title="Awesome ecosystem" url="/usage/projects" button="Read more">
                    Since its release in 2015, spaCy has become an industry standard with a huge
                    ecosystem. Choose from a variety of plugins, integrate with your machine
                    learning stack and build custom components and workflows.
                </LandingCard>
            </LandingGrid>

            <LandingGrid>
                <LandingDemo title="Edit the code &amp; try spaCy">{codeExample}</LandingDemo>

                <LandingCol>
                    <H2>Features</H2>
                    <Features />
                </LandingCol>
            </LandingGrid>

            <LandingBannerGrid>
                <LandingBanner
                    label="NEW"
                    title="Large Language Models: Integrating LLMs into structured NLP pipelines"
                    to="/usage/large-language-models"
                    button="Learn more"
                    small
                >
                    <p>
                        <Link to="https://github.com/explosion/spacy-llm">
                            The spacy-llm package
                        </Link>{' '}
                        integrates Large Language Models (LLMs) into spaCy, featuring a modular
                        system for <strong>fast prototyping</strong> and <strong>prompting</strong>,
                        and turning unstructured responses into <strong>robust outputs</strong> for
                        various NLP tasks, <strong>no training data</strong> required. 
                    </p>
                </LandingBanner>

                <LandingBanner
                    title="Prodigy: Radically efficient machine teaching"
                    label="From the makers of spaCy"
                    to="https://prodi.gy"
                    button="Try it out"
                    background="#f6f6f6"
                    color="#000"
                    small
                >
                    <p>
                        <Link to="https://prodi.gy" noLinkLayout>
                            <ImageFill
                                image={prodigyImage}
                                alt="Prodigy: Radically efficient machine teaching"
                            />
                        </Link>
                    </p>
                    <p>
                        Prodigy is an <strong>annotation tool</strong> so efficient that data
                        scientists can do the annotation themselves, enabling a new level of rapid
                        iteration. Whether you&apos;re working on entity recognition, intent
                        detection or image classification, Prodigy can help you{' '}
                        <strong>train and evaluate</strong> your models faster.
                    </p>
                </LandingBanner>
            </LandingBannerGrid>

            <LandingGrid cols={2} style={{ gridTemplateColumns: '1fr calc(80ch + 14rem)' }}>
                <LandingCol>
                    <H2>Reproducible training for custom pipelines</H2>
                    <p>
                        spaCy v3.0 introduces a comprehensive and extensible system for{' '}
                        <strong>configuring your training runs</strong>. Your configuration file
                        will describe every detail of your training run, with no hidden defaults,
                        making it easy to <strong>rerun your experiments</strong> and track changes.
                        You can use the quickstart widget or the{' '}
                        <Link to="/api/cli#init-config">
                            <InlineCode>init config</InlineCode>
                        </Link>{' '}
                        command to get started, or clone a project template for an end-to-end
                        workflow.
                    </p>
                    <p>
                        <Button to="/usage/training">Get started</Button>
                    </p>
                </LandingCol>
                <LandingCol>
                    <QuickstartTraining />
                </LandingCol>
            </LandingGrid>

            <LandingGrid cols={2}>
                <LandingCol>
                    <Link to="/usage/projects" hidden>
                        <ImageFill
                            image={projectsImage}
                            alt="Illustration of project workflow and commands"
                        />
                    </Link>
                    <br />
                    <br />
                    <br />
                    <Project id="pipelines/tagger_parser_ud" title="Get started">
                        The easiest way to get started is to clone a project template and run it
                        – for example, this template for training a{' '}
                        <strong>part-of-speech tagger</strong> and{' '}
                        <strong>dependency parser</strong> on a Universal Dependencies treebank.
                    </Project>
                </LandingCol>
                <LandingCol>
                    <H2>End-to-end workflows from prototype to production</H2>
                    <p>
                        spaCy&apos;s new project system gives you a smooth path from prototype to
                        production. It lets you keep track of all those{' '}
                        <strong>data transformation</strong>, preprocessing and{' '}
                        <strong>training steps</strong>, so you can make sure your project is always
                        ready to hand over for automation. It features source asset download,
                        command execution, checksum verification, and caching with a variety of
                        backends and integrations.
                    </p>
                    <p>
                        <Button to="/usage/projects">Try it out</Button>
                    </p>
                </LandingCol>
            </LandingGrid>

            <LandingBannerGrid>
                <LandingBanner
                    to="https://explosion.ai/custom-solutions"
                    button="Learn more"
                    background="#E4F4F9"
                    color="#1e1935"
                    small
                >
                    <p>
                        <Link to="https://explosion.ai/custom-solutions" noLinkLayout>
                            <ImageFill
                                image={tailoredPipelinesImage}
                                alt="spaCy Tailored Pipelines"
                            />
                        </Link>
                    </p>
                    <p>
                        <strong>
                            Get a custom spaCy pipeline, tailor-made for your NLP problem by
                            spaCy&apos;s core developers.
                        </strong>
                    </p>
                    <Ul>
                        <Li emoji="🔥">
                            <strong>Streamlined.</strong> Nobody knows spaCy better than we do. Send
                            us your pipeline requirements and we&apos;ll be ready to start producing
                            your solution in no time at all.
                        </Li>
                        <Li emoji="🐿 ">
                            <strong>Production ready.</strong> spaCy pipelines are robust and easy
                            to deploy. You&apos;ll get a complete spaCy project folder which is
                            ready to <InlineCode>spacy project run</InlineCode>.
                        </Li>
                        <Li emoji="🔮">
                            <strong>Predictable.</strong> You&apos;ll know exactly what you&apos;re
                            going to get and what it&apos;s going to cost. We quote fees up-front,
                            let you try before you buy, and don&apos;t charge for over-runs at our
                            end — all the risk is on us.
                        </Li>
                        <Li emoji="🛠">
                            <strong>Maintainable.</strong> spaCy is an industry standard, and
                            we&apos;ll deliver your pipeline with full code, data, tests and
                            documentation, so your team can retrain, update and extend the solution
                            as your requirements change.
                        </Li>
                    </Ul>
                </LandingBanner>
                <LandingBanner
                    to="https://course.spacy.io"
                    button="Start the course"
                    background="#f6f6f6"
                    color="#252a33"
                    small
                >
                    <p>
                        <Link to="https://course.spacy.io" noLinkLayout>
                            <ImageFill
                                image={courseImage}
                                alt="Advanced NLP with spaCy: A free online course"
                            />
                        </Link>
                    </p>
                    <p>
                        In this <strong>free and interactive online course</strong> you’ll learn how
                        to use spaCy to build advanced natural language understanding systems, using
                        both rule-based and machine learning approaches. It includes{' '}
                        <strong>55 exercises</strong> featuring videos, slide decks, multiple-choice
                        questions and interactive coding practice in the browser.
                    </p>
                </LandingBanner>
            </LandingBannerGrid>

            <LandingGrid cols={2} style={{ gridTemplateColumns: '1fr 60%' }}>
                <LandingCol>
                    <H2>Benchmarks</H2>
                    <p>
                        spaCy v3.0 introduces transformer-based pipelines that bring spaCy&apos;s
                        accuracy right up to the current <strong>state-of-the-art</strong>. You can
                        also use a CPU-optimized pipeline, which is less accurate but much cheaper
                        to run.
                    </p>
                    <p>
                        <Button to="/usage/facts-figures#benchmarks">More results</Button>
                    </p>
                </LandingCol>

                <LandingCol>
                    <Benchmarks />
                </LandingCol>
            </LandingGrid>
        </Layout>
    )
}

export default Landing

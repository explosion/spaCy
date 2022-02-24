# Temporary script for debugging purposes
# Delete afterwards -> or convert to actual test
import typer
import spacy
from spacy import displacy
from spacy.tokens import Span


def main(display: str = typer.Argument("ner")):

    if display == "ner":
        print("Testing NER...")
        text = "When Sebastian Thrun started working on self-driving cars at Google in 2007, few people outside of the company took him seriously."
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        displacy.serve(doc, style="ent")
    elif display == "spancat":
        print("Testing SpanCat...")
        nlp = spacy.blank("en")
        text = "Welcome to the Bank of China."
        doc = nlp(text)
        doc.spans["sc"] = [Span(doc, 3, 6, "ORG"), Span(doc, 5, 6, "GPE")]
        doc.spans["custom"] = [Span(doc, 3, 6, "BANK")]
        print(displacy.render(doc, style="span", options={"spans_key": "custom"}))
        displacy.serve(doc, style="span", options={"spans_key": "custom"})
        # text = "Welcome to the Bank of China."
        # text = """Multivariate analysis revealed that septic shock and bacteremia originating
        # from lower respiratory track infection were two independent risk factors for
        # 30 day mortality."""
        # doc = nlp(text)
        # doc.spans["sc"] = [
        #     Span(doc, 0, 2, "METHOD"),
        #     Span(doc, 4, 6, "FACTOR"),
        #     Span(doc, 4, 6, "CONDITION"),
        #     Span(doc, 7, 15, "FACTOR"),
        #     Span(doc, 11, 15, "CONDITION"),
        #     Span(doc, 22, 25, "EFFECT"),
        # ]
        # custom_template = {}

        # # Let's make a thicker border
        # custom_template[
        #     "slice"
        # ] = """
        # <span style="background: {bg}; top: {top_offset}px; height: 7px; border-top-left-radius: 3px; border-bottom-left-radius: 3px; left: -1px; width: calc(100% + 2px); position: absolute;">
        # </span>
        # """

        # # Let's make font-weight: "normal" instead of bold
        # custom_template[
        #     "start"
        # ] = """
        # <span style="background: {bg}; top: {top_offset}px; height: 7px; border-top-left-radius: 3px; border-bottom-left-radius: 3px; left: -1px; width: calc(100% + 2px); position: absolute;">
        #     <span style="background: {bg}; color: rgb(0, 0, 0); top: -0.5em; padding: 2px 3px; z-index: 10; position: absolute; font-size: 0.6em; font-weight: normal; line-height: 1; border-radius: 3px">
        #         {label}{kb_link}
        #     </span>
        # </span>
        # """

        # # Let's make the entities italic
        # custom_template[
        #     "span"
        # ] = """
        # <span style="font-style: italic; font-weight: normal; display: inline-block; position: relative;">
        #     {text}
        #     {span_slices}
        #     {span_starts}
        # </span>
        # """
        # # print(displacy.render(doc, style="span", minify=True))
        # custom_colors = {
        #     "METHOD": "#7aecec",
        #     "FACTOR": "#bfeeb7",
        #     "CONDITION": "#aa9cfc",
        #     "EFFECT": "#ff9561",
        # }
        # displacy.serve(
        #     doc,
        #     style="span",
        #     options={"colors": custom_colors, "template": custom_template},
        # )
    else:
        print(f"Unknown argument: {display}")


if __name__ == "__main__":
    typer.run(main)

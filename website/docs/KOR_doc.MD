<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# spaCy: 산업용 자연어처리

spaCy는 Python 및 Cython의 **향상된 자연어 처리**를 위한 라이브러리입니다.
최신 연구를 기반으로 구축되었으며 처음부터 실제 제품에 사용되도록 설계되었습니다.

spaCy는 [사전에 학습된 파이프라인](https://spacy.io/models)과 함께 제공되며 현재 **60개 이상의 언어**에
대한 토큰화 및 훈련을 지원합니다. 태그 지정, 구문 분석, **명명된 엔티티 인식**, **텍스트 분류**와 BERT와 같은 사전 훈련된 **transformer**를 통한 멀티태스킹 학습뿐만 아니라 
생산 준비가 된 [**사전에 학습된 시스템**](https://spacy.io/usage/training)과 쉬운 모델 패키지, 배포 및 워크 플로우 관리를 위한 최첨단 속도와 **신경망 모델**이 특징입니다. 
spaCy는 MIT 라이선스에 따라 출시된 상용 오픈 소스 소프트웨어입니다.

💫 **3.2 버젼 출시!**
[여기서 릴리스 노트를 확인하세요](https://github.com/explosion/spaCy/releases)

[![Azure 파이프라인](https://img.shields.io/azure-devops/build/explosion-ai/public/8/master.svg?logo=azure-pipelines&style=flat-square&label=build)](https://dev.azure.com/explosion-ai/public/_build?definitionId=8)
[![최근 배포 버젼](https://img.shields.io/github/release/explosion/spacy.svg?style=flat-square&logo=github)](https://github.com/explosion/spaCy/releases)
[![pypi 버젼](https://img.shields.io/pypi/v/spacy.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/spacy/)
[![conda 버젼](https://img.shields.io/conda/vn/conda-forge/spacy.svg?style=flat-square&logo=conda-forge&logoColor=white)](https://anaconda.org/conda-forge/spacy)
[![Python wheels](https://img.shields.io/badge/wheels-%E2%9C%93-4c1.svg?longCache=true&style=flat-square&logo=python&logoColor=white)](https://github.com/explosion/wheelwright/releases)
[![코드 스타일: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)
<br />
[![PyPi 다운로드](https://static.pepy.tech/personalized-badge/spacy?period=total&units=international_system&left_color=grey&right_color=orange&left_text=pip%20downloads)](https://pypi.org/project/spacy/)
[![Conda 다운로드](https://img.shields.io/conda/dn/conda-forge/spacy?label=conda%20downloads)](https://anaconda.org/conda-forge/spacy)
[![spaCy 트위터](https://img.shields.io/twitter/follow/spacy_io.svg?style=social&label=Follow)](https://twitter.com/spacy_io)

## 📖 문서


| 문서              |                                                                |
| -------------------------- | -------------------------------------------------------------- |
| ⭐️ **[spaCy 101]**        | spaCy가 처음이신가요? 여기 알아야 할 모든게 있습니다!()              |
| 📚 **[사용법 가이드]**      | spaCy 사용법과 특징.(설치 및 실행 방법)                             |
| 🚀 **[새로워진 3.0 버젼]**       | 새로운 기능, 이전 버젼과의 비호환성 및 이송 가이드. |
| 🪐 **[프로젝트 템플릿]** | 복사, 수정 및 실행할 수 있는 엔드 투 엔드 워크 플로우.(빠른 시작을 위한 템플릿 제공)            |
| 🎛 **[API 참조]**      | spaCy's API에 대한 자세한 참조.(라이브러리, 파이프라인 구조)                        |
| 📦 **[모델]**            | spaCy용으로 훈련된 파이프라인 다운로드. (영어 등 19개 파이프라인 제공)                  |
| 🌌 **[Universe]**          | spaCy 에코시스템의 플러그인, 확장, 데모 및 책.(spaCy의 모든 것) |
| 👩‍🏫 **[온라인 강좌]**     | 무료 대화형 온라인 강좌에서 spaCy를 배우세요.(비디오 및 설명 제공)        |
| 📺 **[비디오]**            | 비디오 자습서, 대화 등이 포함된 YouTube 채널.      |
| 🛠 **[변경 기록]**          | 변경 사항 및 버전 기록.                                   |
| 💝 **[기여]**        | spaCy 프로젝트와 코드 베이스에 기여하는 방법.        |

[spacy 101]: https://spacy.io/usage/spacy-101
[새로워진 3.0 버젼]: https://spacy.io/usage/v3
[사용법 가이드]: https://spacy.io/usage/
[api 참조]: https://spacy.io/api/
[모델]: https://spacy.io/models
[universe]: https://spacy.io/universe
[비디오]: https://www.youtube.com/c/ExplosionAI
[온라인 강좌]: https://course.spacy.io
[프로젝트 템플릿]: https://github.com/explosion/projects
[변경 기록]: https://spacy.io/usage#changelog
[기여]: https://github.com/explosion/spaCy/blob/master/CONTRIBUTING.md

## 💬 문의할 곳

spaCy 프로젝트는 **[@honnibal](https://github.com/honnibal)**,
**[@ines](https://github.com/ines)**, **[@svlandeg](https://github.com/svlandeg)**,
**[@adrianeboyd](https://github.com/adrianeboyd)** and **[@polm]**(https://github.com/polm)**에 의해 유지됩니다.
이메일을 통한 개별 지원은 제공할 수 없다는 점을 양해바랍니다.
우리는 또한 더 많은 사람들이 도움을 받을 수 있도록 공개적으로 도움을 공유하는 것이 훨씬 더 가치 있다고 믿습니다.

| Type                            | Platforms                               |
| ------------------------------- | --------------------------------------- |
| 🚨 **버그 제보**              | [GitHub Issue Tracker]                  |
| 🎁 **기능 요청 & 아이디어** | [GitHub Discussions]                    |
| 👩‍💻 **사용법 질문**          | [GitHub Discussions] · [Stack Overflow] |
| 🗯 **일반적인 논의**        | [GitHub Discussions]                    |

[github issue tracker]: https://github.com/explosion/spaCy/issues
[github discussions]: https://github.com/explosion/spaCy/discussions
[stack overflow]: https://stackoverflow.com/questions/tagged/spacy

## 특징

- **60개 이상의 언어**를 지원.
- 다른 언어와 작업을 위해 **학습된 파이프라인** 
- BERT와 같은 사전 훈련된 **transformer**
- 사전 훈련된 **단어 벡터** 및 임베딩 지원
- 최첨단 속도
- 생산 준비가 된 **사전에 학습된 시스템**
- 언어 기반 **토큰화**
- 명명된 **엔티티 인식**, 품사 태깅, 종속성 구문 분석, 문장 분할, **텍스트 분류**, 표제어, 형태학적 분석, 엔티티 연결 등을 위한 구성 요소
- **사용자 정의 구성 요소** 및 속성으로 쉽게 확장 가능
- **PyTorch**, **TensorFlow**와 다른 프레임워크의 사용자 정의 모델 지원
- 구문 및 NER을 위한 **비주얼라이저** 내장
- 쉬운 **모델 패키징**, 배포 및 워크플로 관리
- 견고하고 엄격하게 평가된 정확도

📖 **자세한 사항은 여기를 참고하세요
[facts, figures and benchmarks](https://spacy.io/usage/facts-figures).**

## ⏳ spaCy 설치

자세한 설치 방법은 [documentation](https://spacy.io/usage)을 참고하세요.

- **운영체제**: macOS / OS X · Linux · Windows (Cygwin, MinGW, Visual Studio)
- **Python 버전**: Python 3.6+ (only 64 bit)
- **Package 관리자**: [pip] · [conda] (via `conda-forge`)

[pip]: https://pypi.org/project/spacy/
[conda]: https://anaconda.org/conda-forge/spacy

### pip

pip을 사용하면, spaCy release를 소스 패키지 및 binary wheel로사용할 수 있습니다. spaCy 및 해당 종속성을 설치하기 전에, `pip`, `setuptools` 및 `wheel`이 최신 번전인지 확인하세요. 

```bash
pip install -U pip setuptools wheel
pip install spacy
```

표제어 지정 및 정규화를 위한 추가 데이터 테이블을 설치하려면 `pip install spacy[lookups]`를 실행하거나 [`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data)를 별도로  설치할 수 있습니다. lookups 패키지는 표제어 데이터로 빈 모델을 생성하고, 아직 사전 훈련된 모델과 함께 제공되지 않고 타사 라이브러리에서 제공되지 않는 언어로 표제어를 처리하는 데 필요합니다.

아래와 같이 pip를 사용할 때 일반적으로 시스템 상태 수정을 피하기 위해 가상 환경에 패키지를 설치하는 것이 좋습니다.

```bash
python -m venv .env
source .env/bin/activate
pip install -U pip setuptools wheel
pip install spacy
```

### conda

`conda-forge` 채널을 통해 `conda`에서 spaCy를 설치할 수도 있습니다. build recipe 및 구성을 포함한 공급 방식에 대해서는 [this repository](https://github.com/conda-forge/spacy-feedstock)를 확인하세요.

```bash
conda install -c conda-forge spacy
```

### spaCy 업데이트

spaCy에 대한 일부 업데이트는 새로운 통계 모델을 다운로드해야 할 수 있습니다. spaCy v2.0 이상을 실행하는 경우, `validate`명령을 사용하여 설치된 모델이 호환되는지 확인합니다. 호환되지 않는 경우, 업데이트 방법에 대한 세부 정보를 볼 수 있습니다.

```bash
pip install -U spacy
python -m spacy validate
```

특정한 모델을 학습한 경우, training 및 runtime 입력이 일치해야 합니다. spaCy를 업데이트한 후에는 **모델을 새 버전으로 재교육**하는 것이 좋습니다.

📖 **spaCy 2.x에서 spaCy 3.x로 업그레이드하는 방법에 대한 자세한 내용은 [migration guide](https://spacy.io/usage/v3#migrating)을 보세요.**

## 📦 모델 패키지 다운로드

spaCy용으로 훈련된 파이프라인은 **Python packages**로 설치할 수 있습니다. 이는 다른 모듈과 마찬가지로 애플리케이션의 구성 요소임을 의미합니다. 모델은 spaCy의 [`download`](https://spacy.io/api/cli#download) 명령을 사용하거나, pip가 경로나 URL을 가리키도록 하여 수동으로 설치할 수 있습니다.

| Documentation              |                                                 |
| -------------------------- | ----------------------------------------------- |
| **[Available Pipelines]**  | 자세한 파이프라인 설명, 정확도 수치 및 벤치마크 |
| **[Models Documentation]** | 자세한 사용법 및 설치 지침                      |
| **[Training]**             | 데이터에 대한 자체 파이프라인을 훈련하는 방법   |

[available pipelines]: https://spacy.io/models
[models documentation]: https://spacy.io/usage/models
[training]: https://spacy.io/usage/training

```bash
# Download best-matching version of specific model for your spaCy installation
python -m spacy download en_core_web_sm

# pip install .tar.gz archive or .whl from path or URL
pip install /Users/you/en_core_web_sm-3.0.0.tar.gz
pip install /Users/you/en_core_web_sm-3.0.0-py3-none-any.whl
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0.tar.gz
```

### 모델 로드 및 사용

모델을 로드하려면, 모델 이름 또는 모델 데이터 디렉토리 경로와 함께  [`spacy.load()`](https://spacy.io/api/top-level#spacy.load)를 사용하세요.

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("This is a sentence.")
```

전체 이름을 통해 직접 모델을 `import`한 다음 인수 없이 `load()` 메서드를 호출할 수도 있습니다.

```python
import spacy
import en_core_web_sm

nlp = en_core_web_sm.load()
doc = nlp("This is a sentence.")
```

📖 **자세한 정보와 예시는 [models documentation](https://spacy.io/docs/usage/models)를 확인하세요.**

## ⚒ 소스에서 컴파일하기
spaCy를 설치하는 또다른 방법은 [GitHub repository](https://github.com/explosion/spaCy)를 clone하여 소스에서 빌드하는 것입니다. 이는 코드의 베이스를 변경하기 위한 일반적인 방법입니다. 헤더 파일, 컴파일러, [pip](https://pip.pypa.io/en/latest/installing/), [virtualenv](https://virtualenv.pypa.io/en/latest/) 및 [git](https://git-scm.com)을 포함한 Python distribution로 구성된 개발 환경이 설치되었는지 확인해야 합니다. 이중 컴파일러 부분이 가장 까다로운 부분입니다. 어떻게 하는지는 각 시스템에 따라 다릅니다.   
플랫폼	
우분투	시스템 수준의 의존성을 설치
`apt-get: sudo apt-get install build-essential python-dev git`
Mac	“Command Line Tools”를 포함한 최신 버전의 XCode를 설치합니다. macOS와 OS X는 파이썬과 깃이 미리 설치되어 제공됩니다. 
Windows	파이썬 interpreter를 실행하는데 사용되는 버전에 맞는 Visual C++ Build Tools 또는 Visual Studio Express의 버전을 설치
자세한 내용들과 설명은 소스에서 spaCy를 컴파일하는 방법과 퀵스타트 위젯을 통해 여러분의 플랫폼과 파이썬 버전에 적합한 문서를 통해 확인해주세요. 
| Platform    |                                                                                                                                                                                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ubuntu**  | 시스템 수준의 의존성을 설치 `apt-get`: `sudo apt-get install build-essential python-dev git` .                                                                                                                                                            |
| **Mac**     | “Command Line Tools”를 포함한 최신 버전의 [XCode](https://developer.apple.com/xcode/)를 설치.                             |
| **Windows** | 파이썬 interpreter를 실행하는데 사용되는 버전에 맞는 [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 또는 [Visual Studio Express](https://visualstudio.microsoft.com/vs/express/)의 버전을 설치. |

자세한 내용들과 설명은 [compiling spaCy from source](https://spacy.io/usage#source)과 [quickstart widget](https://spacy.io/usage#section-quickstart)을 통해 여러분의 플랫폼과 파이썬 버전에 적합한 문서를 통해 확인해주세요. 

```bash
git clone https://github.com/explosion/spaCy #spaCy 클론하기
cd spaCy #디렉토리로 이동

python -m venv .env #.env에 환경 조성
source .env/bin/activate #가상 env 활성화

# make sure you are using the latest pip
python -m pip install -U pip setuptools wheel #빌드 도구 설치 및 업데이트

pip install -r requirements.txt #requirements 설치하기
pip install --no-build-isolation --editable . #spaCy 컴파일하고 설치하기
```

추가적인 설치:
```bash
pip install --no-build-isolation --editable .[lookups,cuda102]
```


**개발자들을 위한 추가적인 옵션**

추가적인 옵션이 소스코드를 수정하고 자주 컴파일링하는 spaCy 개발자들에게 유용할 것입니다. 

-	수정 가능한 모드로 설치하기. .py 파일에 수정은 파일이 저장되면 반영이 되지만, Cython 파일 (.pxd, .pyx)에 수정은 pip install 또는 python setup.py build_ext 명령이 다시 실행되어야 합니다. 수정 가능한 모드 설치하기 전에, 기존의 설치의 흔적들을 모두 지워야 해서 여러 번 실행해야 하기 때문에 pip uninstall spacy로 기존의 설치가 제거되어야 합니다. 
```bash
pip install -r requirements.txt
pip install --no-build-isolation --editable .
```

-	N개의 CPU를 병렬적으로 빌드하여 컴파일 속도를 높이고 수정 가능한 모드로 설치합니다. 

```bash
pip install -r requirements.txt
python setup.py build_ext --inplace -j N
python setup.py develop
```

## 🚦 테스트 실행

spaCy는 [extensive test suite](spacy/tests)을 제공합니다. 테스트를 실행하려면, 일반적으로 레포지토리를 클론하고 소스에서 spaCy를 구축해야 합니다. 이는 또한 requirements.txt에 정의된 필수 개발 의존성과 테스트 유틸리티를 설치할 것입니다. 
그 대신에, spaCy 패키지 안에서 테스트에 대해서 pytest를 실행할 수 있습니다. spaCy의 [`requirements.txt`](requirements.txt)를 통해서 테스트 유틸리티를 설치하는 것 또한 잊지 마십시오:

```bash
pip install -r requirements.txt
python -m pytest --pyargs spacy
```

spaCy 디렉토리에서 pytest를 부르는 것은 기본적인 테스트만 실행할 것입니다. –slow 플래그는 선택 사항이며 시간이 더 걸리는 추가적인 테스트를 활성화합니다.

```bash
python -m pip install -U pytest               # pytest 업데이트
python -m pytest --pyargs spacy               # 기본적인 테스트
python -m pytest --pyargs spacy --slow        # 기본적인 테스트와 추가적인 테스트들
```

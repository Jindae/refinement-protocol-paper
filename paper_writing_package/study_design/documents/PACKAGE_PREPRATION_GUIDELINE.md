# Paper Writing Package 및 Replication Package 작성 지침

## 1. 목적과 적용 범위

연구가 진행되는 동안 설계 문서, 실행 코드, 설정 파일, raw data, 로그, 임시 분석, 오류가 포함된 실행 결과, 재실행 결과, 정제 데이터, 표와 그림, 의사결정 기록 등이 계속 생성된다. 이러한 자료는 연구 과정을 추적하고 오류의 원인을 확인하는 데 필요하므로 가능한 한 보존해야 한다.

그러나 연구 과정에서 생성된 모든 자료를 그대로 논문 작성이나 공개 재현에 사용하면 다음 문제가 발생할 수 있다.

- 폐기된 설계와 최종 설계가 섞인다.
- 오류가 포함된 결과와 논문에 사용한 결과를 구분하기 어렵다.
- 어떤 수치가 어떤 데이터와 스크립트에서 생성되었는지 추적하기 어렵다.
- 내부 메모, 민감 정보, 불필요한 로그가 공개 자료에 포함될 수 있다.
- 외부 사용자가 논문 결과를 재현하는 데 필요한 핵심 자료를 찾기 어렵다.

이를 방지하기 위해 연구 자료를 다음 세 범주로 구분하여 관리한다.

1. **Working Research Materials**: 연구 수행 과정에서 생성된 전체 작업 자료
2. **`paper_writing_package`**: 최종 채택한 연구 설계와 결과를 논문 작성에 필요한 맥락과 함께 정리한 내부 자료
3. **`replication_package`**: 논문에 보고된 실험과 결과를 재현하는 데 필요한 자료만 포함한 공개용 자료

이 지침은 특정 연구 주제나 실험 방법에 한정되지 않는다. 소프트웨어공학 실험, 머신러닝 평가, 사용자 연구, 데이터 분석, 시뮬레이션, 도구 비교 등 코드와 데이터를 사용하여 결과를 생성하는 실증 연구 전반에 적용할 수 있다.

---

## 2. 세 자료 범주의 역할

| 구분 | 주요 목적 | 포함 범위 | 정제 수준 | 주요 사용자 |
|---|---|---|---|---|
| **Working Research Materials** | 연구 이력 보존, 오류 조사, 재실행, 설계 변경 추적 | 성공 및 실패 실행, 임시 코드, 전체 로그, 폐기된 분석, 중간 의사결정 | 낮음 | 연구 수행자 |
| **`paper_writing_package`** | 논문 작성, 결과 해석, 내부 검토 지원 | 최종 설계, 최종 데이터, 주요 결과, 분석 근거, 필요한 의사결정 맥락 | 중간에서 높음 | 논문 저자, 공동연구자, 내부 검토자 |
| **`replication_package`** | 논문에 보고된 결과의 외부 재현 지원 | 최종 실행 코드, 설정, 논문에 사용한 데이터, 분석 및 산출물 생성 스크립트 | 매우 높음 | 리뷰어, 독자, 후속 연구자 |

세 범주는 서로 다른 목적을 가진다.

- Working Research Materials는 연구 과정 전체를 보존하기 위한 공간이므로 복잡하고 중복될 수 있다.
- `paper_writing_package`는 논문 작성에 필요한 충분한 맥락을 유지하지만, 최종 결과와 무관한 시행착오를 제거한다.
- `replication_package`는 연구 과정을 설명하는 내부 기록이 아니라, 논문에 포함된 결과를 재현하는 데 필요한 공개 산출물이다.

`paper_writing_package`와 `replication_package`는 Working Research Materials의 단순 복사본으로 만들지 않는다. 각 패키지는 명시적인 포함 기준을 통과한 자료만 선별하여 구성한다.

---

## 3. 공통 관리 원칙

### 3.1 원본 자료의 불변성

Raw data, 원시 로그, 원본 응답, 실행 결과와 같은 원본 자료는 생성 후 직접 수정하지 않는다.

오류 수정, 형식 변환, 값 보정이 필요한 경우 다음 원칙을 따른다.

- 원본은 그대로 보존한다.
- 수정된 자료는 별도의 derived artifact로 생성한다.
- 변환 과정은 가능한 한 스크립트로 구현한다.
- 입력 파일, 출력 파일, 실행 명령, 설정, 생성 시간을 기록한다.
- 수작업 보정이 불가피하면 원본 값, 수정 값, 수정 이유, 검토자를 별도 기록한다.

### 3.2 실행 단위의 식별

각 실험 또는 데이터 처리 실행에는 고유한 식별자를 부여한다. 동일한 설정을 재실행하더라도 기존 결과를 덮어쓰지 않는다.

실행 기록에는 연구 유형에 따라 다음 정보를 포함한다.

- 실행 식별자
- 실행 날짜와 시간
- 사용한 코드 revision 또는 commit
- 입력 데이터와 버전
- 실험 대상 시스템, 모델, 도구 또는 알고리즘의 식별 정보
- 실행 설정과 주요 parameter
- software 및 hardware environment
- random seed 또는 비결정성 관련 설정
- 실행 상태
- 제외 여부와 제외 사유
- 대체 실행이 있는 경우 해당 식별자

실행 상태는 최소한 다음과 같이 구분하는 것이 좋다.

- `in_progress`: 실행 중
- `completed`: 실행은 완료되었으나 최종 채택 여부 미결정
- `invalid`: 오류나 설계 위반으로 사용할 수 없음
- `superseded`: 새로운 실행이나 분석으로 대체됨
- `accepted`: 최종 분석과 논문에 사용하기로 승인됨

논문 결과에는 원칙적으로 `accepted` 상태의 실행만 사용한다.

### 3.3 데이터 계보 유지

논문에 사용한 모든 수치, 표, 그림은 최종 raw data까지 역추적할 수 있어야 한다.

각 정제 데이터와 결과에는 다음 연결 정보가 필요하다.

- source raw data 또는 source run
- 변환 또는 분석 스크립트
- 사용한 설정
- 생성된 날짜
- 검증 상태
- 후속 산출물

Spreadsheet에서 값을 직접 수정하거나 결과를 수작업으로 옮기는 방식은 가능한 한 피한다. 불가피한 경우 동일한 변환을 다시 적용할 수 있는 machine-readable correction record를 제공한다.

### 3.4 최종 채택 자료의 명시

파일이 작업 디렉터리에 존재한다는 이유만으로 논문의 근거로 인정하지 않는다.

자료가 최종 분석에 사용되려면 다음이 명확해야 한다.

- 최종 연구 범위에 포함되는가
- 사용한 설정과 버전을 확인할 수 있는가
- 실행 및 평가가 정상적으로 완료되었는가
- 오류와 누락을 점검했는가
- 이전 결과를 대체하는 자료인지 여부가 명확한가
- 논문에 사용할 자료로 승인되었는가

### 3.5 코드, 데이터, 문서의 버전 일치

논문 작성 시점에 다음 항목이 서로 일치해야 한다.

- 논문에서 설명한 연구 설계
- 실제 실행에 사용한 코드와 설정
- 분석에 사용한 데이터
- 표와 그림 생성에 사용한 스크립트
- 공개 replication package

최종 제출 또는 공개 시에는 commit, tag, release version과 checksum을 고정한다.

### 3.6 공개 자료는 allowlist 방식으로 구성

공개 패키지는 내부 작업 디렉터리에서 불필요한 파일을 삭제하는 방식보다, 공개에 필요한 파일만 별도 디렉터리로 복사하거나 export하는 방식으로 구성한다.

이를 통해 다음 자료가 실수로 공개되는 것을 줄일 수 있다.

- credential과 secret
- 개인 정보
- 내부 서버 주소와 경로
- 폐기된 결과
- 불필요한 로그
- 라이선스상 재배포할 수 없는 자료

---

## 4. Working Research Materials 관리 지침

Working Research Materials는 연구 과정의 완전한 이력을 보존하는 내부 작업 공간이다.

### 4.1 포함할 수 있는 자료

- 초기 및 변경된 연구 설계
- 실행 코드의 모든 주요 버전
- pilot study와 exploratory analysis
- 성공 및 실패 실행 결과
- debug logs와 오류 기록
- 재실행 및 대체 실행 결과
- 정제 전후의 데이터
- 분석 스크립트의 중간 버전
- 가설, 메모, 회의 기록, 결정 과정
- 폐기된 결과와 폐기 사유

### 4.2 관리 원칙

- 기존 파일을 덮어쓰기보다 새로운 식별자나 version으로 저장한다.
- 오류가 확인된 자료도 삭제하지 않고 상태와 사유를 기록한다.
- 최종 결과와 중간 결과를 디렉터리 또는 manifest에서 구분한다.
- 대용량 자료는 별도 storage에 보관하더라도 위치와 checksum을 기록한다.
- 민감 정보는 가능한 한 데이터와 분리하여 secret manager 또는 environment variable로 관리한다.

Working Research Materials는 공개용 자료가 아니므로 정제 수준이 낮을 수 있다. 그러나 향후 오류 조사와 재분석이 가능하도록 최소한의 식별 정보와 계보는 유지해야 한다.

---

## 5. `paper_writing_package` 작성 지침

### 5.1 목적

`paper_writing_package`는 논문 저자가 최종 연구 설계, 실행 조건, 분석 방법, 주요 결과와 해석에 필요한 맥락을 한곳에서 확인할 수 있도록 구성한 내부 자료다.

논문의 주요 주장과 수치는 이 패키지 안의 자료를 통해 근거를 확인할 수 있어야 한다. 공개용 최소 패키지가 아니므로 replication package보다 더 많은 설명과 맥락을 포함할 수 있지만, Working Research Materials의 전체 이력을 그대로 포함해서는 안 된다.

### 5.2 포함해야 하는 내용

#### 연구 개요와 최종 설계

- 최종 연구 배경과 목적
- 최종 research questions 또는 hypotheses
- 최종 실험 설계와 비교 조건
- 대상 데이터, 시스템, 도구, 모델 또는 참가자 선정 기준
- 측정 항목과 metric 정의
- 분석 방법과 통계 계획
- inclusion 및 exclusion criteria
- 최종 연구 범위와 주요 제한 사항

#### 실험 및 분석 설정

- 사용한 소프트웨어와 정확한 version
- 실행 대상의 identifier와 revision
- 주요 parameter와 configuration
- hardware 및 operating environment
- 입력 데이터의 version과 구성
- prompt, questionnaire, task instruction 또는 기타 실험 자극물
- timeout, retry, preprocessing, parsing, evaluation 설정
- random seed와 비결정성 처리 방법

#### 최종 raw data

- 논문 결과에 실제로 사용한 accepted run 또는 accepted observation의 raw data
- 원본 로그와 평가 결과
- 원본 입력과 출력의 대응 정보
- 실행 및 측정 metadata
- 누락, 실패, 제외 상태를 확인할 수 있는 기록

Raw data가 크거나 라이선스상 복사가 어려운 경우에는 immutable storage location, exact identifier, checksum, retrieval instruction을 기록할 수 있다.

#### 정제 데이터

- 최종 분석 단위로 정리된 canonical dataset
- raw data에서 생성된 intermediate dataset
- metric 계산 입력
- 통계 분석 입력
- 표와 그림의 source data
- 제외와 보정이 반영된 최종 데이터

#### 분석 결과

- research question별 주요 결과
- summary statistics
- statistical test 및 confidence interval 결과
- sensitivity 또는 robustness analysis
- 최종 표와 그림
- 논문 수치의 검증 기록

#### 분석 및 산출물 생성 스크립트

- raw data 정제 스크립트
- metric 계산 스크립트
- statistical analysis scripts
- table generation scripts
- figure generation scripts
- 실행 명령과 필요한 설정
- 주요 산출물 검증 스크립트

#### 논문 작성에 필요한 맥락

- 각 research question과 결과 자료의 연결
- 결과 해석에 필요한 데이터 또는 실험 조건의 특성
- 최종 설계와 구현에서 내린 주요 결정
- 데이터 제외, 평가 기준 변경, 재실행이 필요했던 이유
- threats to validity와 limitations 후보
- 일관되게 사용할 용어와 표기
- 논문 결과와 source artifact의 대응 관계

최종 결정 기록은 논문을 이해하는 데 필요한 정보에 집중한다. 채택하지 않은 모든 대안을 시간순으로 나열할 필요는 없다. 다만 최종 결과의 범위, 데이터 구성, 평가 방법에 영향을 준 결정은 근거와 적용 범위를 남긴다.

### 5.3 제외해야 하는 내용

원칙적으로 다음 자료는 `paper_writing_package`에 포함하지 않는다.

- 최종 연구 범위와 무관한 pilot study
- 명백한 구현 오류로 생성된 전체 raw data
- 논문에 사용하지 않는 폐기된 분석 결과
- 중복된 임시 파일과 전체 debug log
- superseded code와 document의 모든 세부 버전
- 정리되지 않은 brainstorming과 개인 메모
- API key, access token, password, 개인 계정 정보
- 공개 또는 공동 사용이 불가능한 민감 자료
- cache, virtual environment, 다운로드한 dependency와 model weight

오류나 폐기된 실행이 최종 결과의 inclusion 또는 exclusion을 이해하는 데 필요하다면 원본 전체 대신 간결한 decision record를 포함한다. Decision record에는 문제, 영향 범위, 처리 방법, 대체 자료를 기록한다.

### 5.4 권장 디렉터리 구조

`paper_writing_package/` 자체를 현재 authoring snapshot의 루트로 사용한다. Package ID를
이름으로 한 하위 디렉터리나 `latest/` 포인터를 추가하지 않는다. 저자는 이 디렉터리를
열었을 때 항상 현재 `README.md`, 설계, 설정, 데이터, 분석, 결과 및 provenance를 바로
확인할 수 있어야 한다.

새 snapshot은 별도의 실행 attempt 안에서 고유 package ID로 생성하고 독립 검증한 뒤에만
이 루트를 교체한다. 루트에는 이전 snapshot의 전체 복사본을 함께 보관하지 않는다. 현재
내용과 이전 내용의 변경 이력은 Git이 추적하고, package ID, source commit, manifest hash,
검증 및 교체 시각은 package manifest와 durable attempt에 기록한다. Working Research
Materials의 원자료와 실행 기록은 이 교체와 무관하게 불변으로 보존한다.

```text
paper_writing_package/
├── README.md
├── study_design/
│   ├── project_overview.md
│   ├── research_questions.md
│   ├── methodology.md
│   ├── measures_and_metrics.md
│   └── analysis_plan.md
├── experiment_setup/
│   ├── configurations/
│   ├── instruments_or_prompts/
│   ├── environment.md
│   └── inclusion_exclusion.md
├── data/
│   ├── raw_accepted/
│   ├── canonical/
│   └── derived/
├── analysis/
│   ├── scripts/
│   ├── statistical_outputs/
│   └── validation/
├── results/
│   ├── research_questions/
│   ├── tables/
│   └── figures/
├── decisions/
│   ├── final_design_decisions.md
│   ├── data_decisions.md
│   └── known_limitations.md
└── provenance/
    ├── run_manifest.csv
    ├── data_lineage.csv
    └── paper_result_manifest.csv
```

실제 연구에 맞게 디렉터리 이름은 변경할 수 있다. 다만 설계, 설정, 데이터, 분석, 결과, 결정 기록, provenance는 가능한 한 분리한다.

### 5.5 `paper_result_manifest`

논문에 사용할 주요 결과를 추적하기 위한 manifest를 유지한다.

권장 항목은 다음과 같다.

- result identifier
- 관련 research question 또는 hypothesis
- 논문의 section, table 또는 figure
- 분석 대상 또는 조건
- source raw data
- canonical data file
- analysis script
- generated output
- validation status
- 관련 commit 또는 release

이 manifest를 통해 논문 수치가 어떤 데이터와 스크립트에서 생성되었는지 확인할 수 있어야 한다.

---

## 6. `replication_package` 작성 지침

### 6.1 목적

`replication_package`는 논문에 보고된 실험과 분석 결과를 외부 연구자가 이해하고 재현할 수 있도록 제공하는 공개용 패키지다.

이 패키지의 목적은 연구 과정의 모든 시행착오를 공개하는 것이 아니다. 논문에 포함된 결과를 생성하는 데 필요한 최종 자료와 절차를 완전하고 정제된 형태로 제공하는 것이다.

실험 전체를 다시 실행하는 비용이 큰 경우에는 다음 두 재현 경로를 구분하여 제공한다.

1. **Experiment reproduction**: 원본 입력에서 실험 또는 측정을 다시 실행하여 raw data를 재생성하는 절차
2. **Result reproduction**: 제공된 raw data에서 정제 데이터, metric, 통계 결과, 표와 그림을 다시 생성하는 절차

최소한 두 번째 경로는 독립적으로 실행 가능해야 한다.

### 6.2 포함해야 하는 내용

#### README

`README.md`에는 최소한 다음 내용을 포함한다.

- 연구와 replication package의 범위
- 논문과 package artifact의 대응 관계
- directory structure
- hardware 및 software requirements
- environment setup
- 외부 데이터와 도구의 획득 방법
- exact version 또는 revision
- 실험 실행 명령
- raw-data 처리 및 분석 명령
- 표와 그림 생성 명령
- expected output files
- 주요 resource requirement와 예상 실행 범위
- data schema와 file format
- known limitations
- licensing 및 citation information

명령은 가능하면 repository root에서 실행할 수 있어야 한다. 개인 서버의 absolute path, private URL, 내부 storage를 전제로 해서는 안 된다.

#### 최종 실행 코드

- 논문에 보고된 실험 또는 데이터 수집 절차를 수행하는 코드
- 입력 준비와 preprocessing 코드
- 결과 parsing과 normalization 코드
- 평가 또는 측정 코드
- 오류 기록, timeout, retry 처리
- configuration loader
- 실행 entry point

공개 코드는 논문 결과를 생성한 최종 구현을 기준으로 정리한다. 내부 환경에 종속된 부분을 제거하거나 공개용으로 재구성할 수 있지만, 실험의 의미와 결과 생성 절차가 달라져서는 안 된다.

#### 설정과 실험 자료

- 실행 조건별 configuration
- prompt, questionnaire, task description, template 또는 test input
- generation, optimization 또는 sampling configuration
- preprocessing 및 evaluation setting
- inclusion 및 exclusion list
- random seed 또는 비결정성 관련 설정

#### 논문에 사용한 raw data

- 논문 결과에 사용한 accepted raw data
- 입력과 출력의 연결 정보
- task, sample 또는 observation 수준의 평가 결과
- 실행 metadata
- 실패, 누락, 제외 상태

오류로 폐기한 실행, 재실행 전 자료, 논문에 사용하지 않은 pilot data는 포함하지 않는다.

Raw data를 직접 배포할 수 없는 경우에는 다음을 제공한다.

- 공식 다운로드 또는 접근 위치
- exact version 또는 identifier
- checksum
- retrieval script
- 필요한 변환 절차
- 재배포하지 못하는 이유

#### 정제 데이터

- accepted raw data에서 생성한 canonical dataset
- metric 또는 statistical analysis input
- 논문 표와 그림의 source data
- 주요 집계 결과

정제 데이터는 제공된 스크립트를 사용하여 raw data에서 다시 생성할 수 있어야 한다.

#### 분석 및 산출물 생성 스크립트

- data preparation
- metric calculation
- statistical analysis
- robustness 또는 sensitivity analysis
- table generation
- figure generation
- paper-reported result validation

표와 그림의 데이터 값은 수작업 편집 없이 스크립트로 생성해야 한다. 논문 형식에 맞춘 시각적 조정이 필요한 경우에도 source data와 생성 스크립트를 제공한다.

#### Expected outputs와 검증 자료

- 주요 summary results
- expected sample 또는 task counts
- 논문에 포함된 table data
- figure source data 또는 생성된 figure
- validation report
- 필요한 경우 checksum 또는 허용 오차

외부 사용자가 자신의 실행 결과를 expected output과 비교하여 pipeline이 올바르게 수행되었는지 확인할 수 있어야 한다.

#### 환경 및 라이선스 정보

- dependency specification
- container 또는 environment definition
- system requirements
- source code license
- third-party data와 dependency의 license
- citation information

### 6.3 제외해야 하는 내용

다음 자료는 `replication_package`에 포함하지 않는다.

- API key, password, token, SSH configuration
- 개인 이름, 계정 정보, private host name과 IP
- 내부 directory path와 private storage URL
- 폐기된 script와 invalid run
- 중간 brainstorming과 내부 의사결정 토론
- 논문에 포함하지 않은 pilot result
- 불필요한 full debug log
- cache, virtual environment, downloaded dependency, model weight
- 재배포가 허용되지 않은 데이터
- 개인정보 또는 민감 정보
- 논문 결과 재현에 필요하지 않은 내부 관리 자료

원본 내부 코드나 데이터를 그대로 공개할 필요는 없다. 공개용으로 정리하거나 민감한 부분을 제거한 버전을 사용할 수 있다. 다만 공개된 자료만으로 논문에 포함된 결과를 동일한 절차로 재현할 수 있어야 한다.

### 6.4 권장 디렉터리 구조

```text
replication_package/
├── README.md
├── LICENSE
├── CITATION.cff
├── environment/
│   ├── requirements.txt
│   ├── environment.yml
│   ├── container_definition
│   └── system_requirements.md
├── configs/
├── instruments_or_prompts/
├── scripts/
│   ├── run_experiments/
│   ├── prepare_data/
│   ├── evaluate/
│   ├── analyze/
│   ├── make_tables/
│   └── make_figures/
├── data/
│   ├── raw/
│   ├── processed/
│   └── schemas/
├── results/
│   ├── tables/
│   ├── figures/
│   └── expected/
├── manifests/
│   ├── runs.csv
│   ├── files.csv
│   └── paper_results.csv
└── docs/
    ├── data_dictionary.md
    ├── experiment_reference.md
    └── reproduction_workflows.md
```

연구 유형에 따라 사용하지 않는 디렉터리는 생략할 수 있다.

---

## 7. Package 승격 절차

### 7.1 Working Research Materials에서 `paper_writing_package`로

자료는 다음 조건을 충족할 때 `paper_writing_package`에 포함한다.

- 최종 연구 범위에 포함된다.
- 사용한 입력, 설정, 버전을 확인할 수 있다.
- 실행 또는 수집이 정상적으로 완료되었다.
- 결과와 데이터가 검증되었다.
- 최종 분석에 사용할지 여부가 결정되었다.
- source와 변환 과정이 추적 가능하다.
- superseded artifact와 구분된다.
- 민감 정보가 제거되었거나 접근이 제한된다.

### 7.2 `paper_writing_package`에서 `replication_package`로

자료는 다음 조건을 충족할 때 `replication_package`에 포함한다.

- 논문에 보고된 결과와 직접 관련된다.
- 외부 사용자가 이해할 수 있는 형식으로 정리되었다.
- private dependency 없이 실행할 수 있다.
- 필요한 configuration과 documentation이 제공된다.
- 민감 정보와 불필요한 내부 정보가 제거되었다.
- license와 redistribution 조건을 충족한다.
- clean environment에서 재현 검증을 통과했다.

`paper_writing_package`의 모든 파일을 replication package로 옮기지 않는다. 공개에 필요한 파일을 allowlist로 지정하여 export한다.

---

## 8. 설계 또는 결과 변경 시 업데이트 절차

최종 채택한 설계, 데이터 또는 결과가 변경되면 기존 파일을 조용히 교체하지 않는다.

다음 절차를 따른다.

1. 새로운 실행, 데이터, 분석 결과에 별도 identifier를 부여한다.
2. 기존 자료를 `superseded` 또는 `invalid`로 표시한다.
3. 변경 이유와 영향 범위를 기록한다.
4. 영향을 받은 research question, table, figure, claim을 확인한다.
5. `paper_result_manifest`와 data lineage를 갱신한다.
6. `paper_writing_package`의 설명과 결과를 갱신한다.
7. 공개 package가 존재하면 새로운 version 또는 release를 만든다.
8. 논문 수치, package output, expected result가 일치하는지 다시 검증한다.

최종 submission 또는 release 시점에는 package version, repository tag, commit hash를 고정한다.

---

## 9. Replication Package 검증 절차

### 9.1 Clean-environment reproduction

- 새 clone, clean container 또는 새로운 environment에서 실행한다.
- README에 기록한 명령만 사용한다.
- 기존 cache나 private directory에 의존하지 않는다.
- raw-to-processed pipeline을 실행한다.
- metric, statistical result, table, figure를 재생성한다.

### 9.2 결과 일치 확인

연구에 따라 다음 항목을 확인한다.

- 입력 및 분석 대상 수
- 포함 및 제외 수
- 주요 summary statistics
- 주요 metric
- statistical test와 confidence interval
- table source values
- figure source values
- expected file과 checksum

환경 차이로 exact byte match가 어려운 경우 허용 오차와 비교 방법을 명시한다.

### 9.3 민감 정보 검사

- secret scanner를 실행한다.
- environment file과 log를 검사한다.
- absolute path를 검사한다.
- 사용자 이름, host name, private URL을 검사한다.
- example credential이 실제 값으로 남아 있지 않은지 확인한다.

### 9.4 Completeness 검사

- README의 모든 명령이 실제로 동작하는지 확인한다.
- 참조된 파일이 모두 존재하는지 확인한다.
- raw-to-processed lineage가 끊기지 않는지 확인한다.
- 논문의 주요 표와 그림을 모두 생성할 수 있는지 확인한다.
- 외부 자료의 download instruction과 version이 정확한지 확인한다.

### 9.5 License 검사

- source code license를 명시한다.
- third-party dependency와 data license를 확인한다.
- 재배포가 허용되지 않은 파일을 제거한다.
- 필요한 attribution과 citation을 제공한다.

### 9.6 독립 검토

가능하면 패키지를 작성하지 않은 연구자가 README만 사용하여 재현을 시도한다. 작성자가 암묵적으로 알고 있는 절차가 문서에서 누락되는 문제를 줄일 수 있다.

---

## 10. README 작성 원칙

두 package의 `README.md`는 목적이 다르다.

### `paper_writing_package/README.md`

다음을 빠르게 찾을 수 있어야 한다.

- 최종 연구 범위와 설계 문서
- 논문에 사용한 데이터
- research question별 주요 결과
- 표와 그림의 source
- 주요 결정과 limitation
- 논문 결과의 provenance

### `replication_package/README.md`

다음을 처음 접한 외부 사용자가 수행할 수 있어야 한다.

- 환경 구성
- 필요한 외부 자료 획득
- 실험 재실행
- 제공된 raw data 재분석
- 논문 metric 재계산
- 표와 그림 재생성
- 결과의 정상 생성 여부 확인

README는 내부 용어와 암묵적 지식을 최소화하고, 명령과 예상 결과를 구체적으로 작성한다.

---

## 11. 최종 점검표

### `paper_writing_package`

- [ ] 최종 연구 설계만 명확하게 정리되어 있다.
- [ ] 논문의 주요 주장과 수치를 package 안에서 확인할 수 있다.
- [ ] accepted raw data와 canonical data가 구분되어 있다.
- [ ] 결과를 생성한 스크립트와 설정이 연결되어 있다.
- [ ] 주요 결정과 limitation에 필요한 맥락이 기록되어 있다.
- [ ] 폐기된 시행착오와 불필요한 로그가 제거되어 있다.
- [ ] 논문 결과의 provenance manifest가 존재한다.

### `replication_package`

- [ ] 논문 결과 재현에 필요한 최종 자료만 포함한다.
- [ ] raw data에서 표와 그림까지 자동 생성할 수 있다.
- [ ] 실험 재실행과 결과 재분석 절차가 구분되어 있다.
- [ ] README만으로 clean environment에서 실행할 수 있다.
- [ ] expected outputs와 검증 방법이 제공된다.
- [ ] 민감 정보와 내부 경로가 제거되어 있다.
- [ ] third-party license와 redistribution 조건을 준수한다.
- [ ] package version과 논문에 사용한 version이 일치한다.

---

## 12. 핵심 원칙 요약

- 연구 과정 전체는 Working Research Materials에 보존한다.
- `paper_writing_package`는 최종 연구 설계와 결과를 논문 작성에 충분한 맥락과 함께 정리한다.
- `replication_package`는 논문 결과를 재현하는 데 필요한 최소한의 완전한 자료만 공개한다.
- Raw artifact는 직접 수정하지 않고, 모든 변환은 추적 가능한 방식으로 수행한다.
- 폐기된 실행과 중간 시행착오는 내부 작업 자료에 남기고 공개 package에는 포함하지 않는다.
- 논문 결과의 source data, script, output, paper location을 manifest로 연결한다.
- 공개 package는 allowlist 기반으로 구성하고 clean environment에서 검증한다.
- 논문, `paper_writing_package`, `replication_package`의 결과와 version은 최종 release 시점에 일치해야 한다.

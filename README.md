## 프로젝트 소개
### nlp_analysis.py
- Stanza, Gemini API를 활용한 문장구조 분석 및 번역, 시각화(Google API는 현재 미사용)
### FitnessCenterManagement
- Supabase DB와 smtplib 이메일 송신 모듈을 활용, 회원 출입/예약 관리 및 메일 자동발송 기능 구현
### nos_nieuws_crawling
- RSS 기반 뉴스기사 수집

- Uses official NOS RSS feeds only (no HTML crawling).
- Shows short previews (<=3 sentences / 500 chars) with source links.
- CSV export contains only title, URL, and extracted keywords.
- All article copyrights remain with NOS.

### pygame_mini_game
- 파이썬 Pygame으로 방향키 조작 기반 미니게임 제작


## 사용 라이브러리 및 라이선스

- beautifulsoup4 (v4.12.x): MIT License
  - [라이선스 전문 바로가기] (https://opensource.org/license/mit/)
  - [공식 홈페이지] (https://www.crummy.com/software/BeautifulSoup/)

- matplotlib (v3.x): PSF License
  - [라이선스 전문 바로가기] (https://github.com/matplotlib/matplotlib/blob/main/LICENSE/LICENSE)
  - [공식 홈페이지] (https://matplotlib.org/)

- numpy (v1.26.x): BSD 3-Clause License
  - [라이선스 전문 바로가기] (https://github.com/numpy/numpy/blob/main/LICENSE.txt)
  - [공식 홈페이지] (https://numpy.org/)

- pandas (v2.x): BSD 3-Clause License
  - [라이선스 전문 바로가기] (https://opensource.org/license/bsd-3-clause/)
  - [공식 홈페이지] (https://pandas.pydata.org/)

- pygame (v2.6.1): GNU LGPL v2.1
  - [라이선스 전문 바로가기] (https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)
  - [공식 홈페이지] (https://www.pygame.org)

- python-dotenv (v1.0.x): BSD 3-Clause License
  - [라이선스 전문 바로가기] (https://github.com/theskumar/python-dotenv/blob/main/LICENSE)
  - [공식 홈페이지] (https://pypi.org/project/python-dotenv/)

- requests (v2.31.0): Apache License 2.0
  - [라이선스 전문 바로가기] (https://www.apache.org/licenses/LICENSE-2.0.txt)
  - [공식 홈페이지] (https://requests.readthedocs.io/)

- stanza (v1.8.2): Apache License 2.0
  - [라이선스 전문 바로가기] (https://www.apache.org/licenses/LICENSE-2.0.txt)
  - [공식 홈페이지] (https://stanfordnlp.github.io/stanza/)

- streamlit (v1.35.0): Apache License 2.0
  - [라이선스 전문 바로가기] (https://www.apache.org/licenses/LICENSE-2.0.txt)
  - [공식 홈페이지] (https://streamlit.io/)

- supabase-py (v2.x): MIT License
  - [라이선스 전문 바로가기] (https://github.com/supabase-community/supabase-py/blob/develop/LICENSE)
  - [공식 홈페이지] (https://supabase.com/)


These projects include components licensed under the Apache License, Version 2.0.  
Each such component may have its own copyright and NOTICE file.  
Where required, original NOTICE content is retained in accordance with the license terms.



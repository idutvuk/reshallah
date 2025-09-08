// =======================
//  main.typ — RTU MIREA / ГОСТ template for Typst
// =======================

// ---- Глобальные настройки страницы и текста

#let cfg = (
  paper: "a4",
  margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm),
  font: "Times New Roman",
  size: 14pt,
  leading: 1.5em,        // межстрочный 1.5
  indent: 10mm,          // абзацный отступ
  footnote_size: 12pt,   // сноски 12 pt
  caption_size: 13pt,    // подписи к рисункам/таблицам 13 pt (курсив)
)
// Страница и колонтитул: номер внизу по центру,
// но скрываем на стр. 1, 2 и последней
#set page(
  paper: cfg.paper,
  margin: cfg.margin,
  footer: context {
    let p    = counter(page).get().at(0)
    let last = counter(page).final().at(0)
    if p > 2 and p < last {
      align(center, counter(page).display("1"))
    } else { none }
  },
)



// Русская типографика: шрифт TNR, 14 pt, переносы, «ёлочки»
#set text(
  font: cfg.font,
  size: cfg.size,
  lang: "ru",
  hyphenate: true,
)


// Выровнять по ширине; абзацный отступ 10 мм
// (если у вас Typst ≥ 0.13, можно включить indent для всех абзацев так:
//  #set par(first-line-indent: (amount: cfg.indent, all: true)))
#set par(justify: true, first-line-indent: cfg.indent, leading: cfg.leading)

// Сноски: размер 12 pt и разделительная линия
#show footnote.entry: it => {
  set text(size: cfg.footnote_size)
  line(length: 25%, stroke: 0.5pt)
  v(0.4em)
  it
}

// ---- Заголовки по ГОСТ
// Нумерация разделов "1." "1.1." ...
#set heading(numbering: "1.")

// Заголовок 1 уровня: с новой страницы, ВЕРХНИМ РЕГИСТРОМ, жирный, по центру,
// отступ 10 pt после; также тут же сбрасываем счётчики фигур/таблиц/формул.
#show heading.where(level: 1): it => {
  // сброс счётчиков в начале главы
  counter(figure).update(0)
  counter(figure.where(kind: table)).update(0)
  counter(math.equation).update(0)

  pagebreak()
  set align(center)
  set text(weight: "bold", size: 16pt)
  upper(it.body)
  v(10pt)
}

// Заголовок 2 уровня: жирный, по центру, отступ 10 pt перед основным текстом
#show heading.where(level: 2): it => [
  #set align(center)
  #set text(weight: "bold", size: 14.5pt)
  #it.body
  #v(10pt)
]

// Заголовок 3 уровня: жирный курсив, по левому краю, отступ 10 pt
#show heading.where(level: 3): it => [
  #set align(left)
  #strong[#emph[#set text(size: 14pt); it.body]]
  #v(10pt)
]

// ---- Рисунки / Таблицы / Подписи

// Нумерация фигур (и таблиц) как "глава.порядковый"
// #set figure(numbering: (..n) => {
//   let sec = counter(heading).get()
//   let nums = sec + n
//   nums.pos().map(str).join(".")
// })
#set math.equation(numbering: ("1")) // todo remove

// Подписи к фигурам курсивом 13 pt
#show figure.caption: it => emph(text(size: cfg.caption_size)[#it])

// Таблицы: подпись сверху и выравнивание подписи по правому краю;
// большие таблицы — допускаем разрыв на страницы.
#show figure.where(kind: table): set figure.caption(position: top)
// #show figure.where(kind: table) set figure.caption: it => align(right, emph(text(size: cfg.caption_size)[#it]))
#show figure: set block(breakable: true)


// // ---- Формулы (нумерация по главам, центрирование)
// #set math.equation(numbering: (..n) => {
//   let sec = counter(heading).get()
//   let s = (sec + n).pos().map(str).join(".")
//   "(" + s + ")"
// })
#set math.equation(numbering: ("1")) // todo remove
#show math.equation: set align(center)


// ---- Утилиты для ссылок и неразрывных пробелов

// Сокращённые ссылки "рис. N" и "табл. N"
#let rref = (label) => [рис.~#ref(label, supplement: none)]
#let tref = (label) => [табл.~#ref(label, supplement: none)]
// Ссылка на формулу: только номер в скобках
#let eqref = (label) => ref(label, supplement: none)



#let sig(label: "", width: 6cm) = {
  // signature line with label underneath (in parentheses)
  stack(
    spacing: 0.25em,
    [
      // «__» ______ 2025 г.  (подпись …)
      // date + line + year
      #box(width: width)[«__» #h(0.6em) ______]
    ],
    emph(size: 10.5pt)[(#label)]
  )
}

// Main generator
#let mirea-titlepage(
  // верхняя часть
  coat_of_arms: none,                // например: image("rf-coat.png", width: 2.8cm)
  uni_short: "РТУ МИРЭА",

  institute: none,                   // "Институт информационных технологий (ИТ)"
  department: none,                  // "Кафедра ... (ИнППО)"

  // центральный блок
  doc_type_top: "ОТЧЁТ ПО ПРАКТИЧЕСКИМ РАБОТАМ",
  discipline_prefix: "по дисциплине",
  discipline: "Проектирование информационных систем",
  topic_prefix: "на тему",
  topic: "",                         // например: «Контроль экологической безопасности» ...

  // сведения об авторе/проверившем
  student_label: "Выполнил студент группы",
  group: "ИКБО-00-00",
  student_fio: "И.И. Иванов",

  checker_label_left: "Принял",
  checker_post_left: "Ассистент",
  checker_fio_right: "П.П. Петров",

  // подписи
  left_note: "Практические работы выполнены",
  right_note: "«Зачтено»",
) = {
  set align(center)
  set text(size: 12pt)

  image("mirea-logo.png", width: 0% + 79.37pt)
  v(0.8em)

  // "шапка"
  smallcaps("МИНОБРНАУКИ РОССИИ")
  v(0.4em)
  "Федеральное государственное бюджетное образовательное учреждение высшего образования"
  linebreak()
  strong("«МИРЭА – Российский технологический университет»")
  v(0.35em)
  set text(size:16pt)
  strong("РТУ МИРЭА")
  set text(size:12pt)
  v(0.5em)
  line(length: 100%, stroke: 2pt)
  v(0.9em)

  // институт/кафедра (если заданы)
  institute; v(0.35em)
  department; v(0.9em)

  // центральная часть
  set text(size: 14pt)
  strong(upper(doc_type_top))
  v(0.5em)

  strong[#discipline_prefix «#discipline»]
  v(0.6em)

  if topic != "" {
    set text(size: 14pt)
    topic_prefix
    v(0.2em)
    strong[#topic]
    v(0.2em)
  }

  v(3.5em)

  // блоки слева/справа (как в образце)
  // используем сетку 2 колонки: слева подписи, справа ФИО/роли, выравнивание по краям
  set text(size: 12pt)
  grid(columns: (1fr, 1fr), column-gutter: 2cm)[
    #align(left)[
      #student_label #group
    ]
    #align(right)[
      #student_fio
    ]

    #align(left)[
      #checker_label_left
      #linebreak()
      #emph[#checker_post_left]
    ]
    #align(right)[
      #checker_fio_right
    ]
  ]

  v(4em)

  // даты и подписи (две колонки)
  grid(columns: (1fr, 1fr), column-gutter: 2cm)[
    #align(left)[
      #left_note «\_\_» \_\_\_\_\_\_ 2025 г.
      #linebreak()
      #text(size: 10.5pt)["(подпись студента)"]
    ]
    #align(right)[
      #right_note «\_\_» \_\_\_\_\_\_ 2025 г.
      #linebreak()
      #text(size: 10.5pt)[(подпись руководителя)]
    ]
  ]
  "Москва 2025"

}


#let titlepage(
  uni: "Российский технологический университет (РТУ МИРЭА)",
  institute: none,
  department: none,
  doc_type: "ОТЧЁТ",
  discipline: none,
  work_title: "Название работы",
  author_fio: "И.И. Иванов",
  group: "Группа XX-00",
  supervisor: "И.О. Руководитель",
) = {
  set align(center)
  block(spacing: 1.2em)[
    #smallcaps[#{org}]
    #uni
    #institute
    #department

    #v(8em)

    #strong[#upper(doc_type)]
    #v(0.8em)
    #strong[#work_title]
    #v(0.2em) Дисциплина: #discipline

    #v(6em)

    #align(left)[
      Автор: #author_fio \  Группа: #group \\
      Руководитель: #supervisor
    ]

    #v(6em)

    #city \ #year
  ]

}


// ---- Оглавление (автособираемое)
#let toc_page() = {
  set align(center)
  v(1em)
  set align(left)
  outline()
}

// // =======================
// //     Документ
// // =======================



#mirea-titlepage(
  coat_of_arms: image("mirea-logo.png", width: 2.8cm),
  institute: "Институт информационных технологий (ИТ)",
  department: "Кафедра инструментального и прикладного программного обеспечения (ИнППО)",
  discipline: "Проектирование информационных систем",
  topic: "«Контроль экологической безопасности» (мониторинг загрязнения воздуха и воды, учёт выбросов предприятий)",
  group: "ИКБО-22-22",
  student_fio: "Гиричев А.А.",
  checker_fio_right: "Брагусь Н.В.",
)






#toc_page()

= Введение

Этот шаблон демонстрирует основные требования и автоматизирует их: поля 2 см, шрифт TNR 14 pt, 1.5 интервал, переносы, выравнивание по ширине, абзацный отступ 10 мм, а также нумерацию изображений, таблиц и формул по главам. Между числом и единицей — неразрывный пробел: 36,6°С, 90~%, 1000~кг.

== Пример рисунка и таблицы

См. #rref(<fig:impl>) и #tref(<tbl:stages>).

#figure(
  rect(width: 60%, height: 3cm, fill: luma(220))[ ],
  caption: [Реализация внедрения зависимостей в Spring],
) <fig:impl>

#figure(
  table(
    columns: 3,
    inset: 6pt,
    stroke: 0.5pt,
    [Показатель], [2019 г.], [в % к 2018 г.],
    [Минеральные удобрения, тыс. т], [23588,3], [103,2],
    [Пластмассы, тыс. т], [8759,1], [106,6],
  ),
  caption: [Некоторые производственные показатели],
)

#figure(
  table(
    columns: 2,
    inset: 6pt,
    stroke: 0.5pt,
    [Стадии], [Этапы],
    [1. Формирование требований], [1.1. Обследование; 1.2. Формирование; 1.3. Отчёт],
    [2. Концепция], [2.1. Изучение; 2.2. НИР; 2.3. Варианты; 2.4. Отчёт],
  ),
  caption: [Стадии и соответствующие им этапы],
) <tbl:stages>

== Пример формулы и ссылки

Формулу #eqref(<eq:newton>) применяют в случае …

$ F = m dot a $ <eq:newton>


= #lorem(5)
== #lorem(7)
#lorem(120) (см. @rick)
#figure(
  image("max.png", width: 60%),
  caption: [
    Never gonna give you up!
  ],
) <rick>

== #lorem(10)
Как любил говорить старина Ландау, @landau  --- #lorem(120)


= Заключение

Вот и всё… Неплохая получилась история. @kukhnya:2012 Интересная, весёлая, порой немного грустная, а главное – поучительная…Она научила нас быть смелыми и не бояться вызовов, которые готовит нам жизнь. Помогала нам добиваться поставленных целей несмотря ни на что. И самое важное – она научила нас по-настоящему любить и не сходить с пути, следуя за своей мечтой. #linebreak() 
#set align(center)
#sym.copyright Повар Лавров (@max)
#set align(left)
#figure(
  image("max.png", width: 100%),
  caption: [
    Макс здорового человека
  ],
) <max>

// ГОСТ-стиль
#bibliography(
  "refs.bib",
  title: "СПИСОК ЛИТЕРАТУРЫ", 
  style: "gost-r-705-2008-numeric",
  full: true,
)


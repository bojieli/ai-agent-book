// Web-only replacement for Figure 8-13. The chapter describes an illustrative
// SWE-bench task; these labels deliberately preserve its assumed 4/16 outcome
// rather than presenting the numbers as a measured benchmark result.

const translations = {
  en: {
    title: 'One GRPO step: 16 rollouts of the same SWE-bench task',
    example: 'Hypothetical chapter example',
    taskHeading: 'Same task + initial code',
    taskBug: 'parser.py: empty input raises IndexError',
    taskConstraint: 'The Agent must not modify tests',
    policyHeading: 'Current policy model',
    policyDetail: 'Samples 16 independent attempts',
    rolloutsHeading: '1 · 16 isolated rollouts',
    rolloutsDetail: 'Same initial state · stochastic paths',
    pass: 'pass',
    fail: 'fail',
    summary: 'Assume 4 pass · 12 fail',
    rewardHeading: '2 · Verify and score',
    rewardDetail:
      'Apply each patch in a clean environment; run tests and check the rules',
    rewardPass: 'Pass all tests; tests unchanged → reward 1',
    rewardFail: 'Failed tests or rule violation → reward 0',
    advantageHeading: '3 · Compare within the group',
    advantageMean: 'Group mean = 4/16 = 0.25',
    advantagePass: '4 passing rollouts: above mean → positive advantage',
    advantageFail: '12 failed rollouts: below mean → negative advantage',
    updateHeading: '4 · Update the policy',
    updateDetail: 'Gradient descent + optimizer',
    increase: 'Increase choices from positive-advantage trajectories',
    decrease: 'Decrease choices from negative-advantage trajectories',
    nextStep: 'Updated policy → next step',
    stepSummary:
      'One step: rollout → verification → relative advantage → parameter update → repeat',
  },
  'zh-CN': {
    title: '一个 GRPO step：同一 SWE-bench 任务的 16 次 rollout',
    example: '章节中的假设示例',
    taskHeading: '同一任务 + 初始代码',
    taskBug: 'parser.py：空输入触发 IndexError',
    taskConstraint: 'Agent 不能修改测试',
    policyHeading: '当前策略模型',
    policyDetail: '独立采样 16 次',
    rolloutsHeading: '1 · 16 个隔离的 rollout',
    rolloutsDetail: '初始状态相同 · 采样路径不同',
    pass: '通过',
    fail: '失败',
    summary: '假设 4 条通过 · 12 条失败',
    rewardHeading: '2 · 验证并计算奖励',
    rewardDetail: '在干净环境中应用每个补丁，运行测试并检查规则',
    rewardPass: '全部测试通过且未改测试 → 奖励 1',
    rewardFail: '测试失败或违规 → 奖励 0',
    advantageHeading: '3 · 组内比较',
    advantageMean: '组内平均 = 4/16 = 0.25',
    advantagePass: '4 条通过：高于平均 → 正优势',
    advantageFail: '12 条失败：低于平均 → 负优势',
    updateHeading: '4 · 更新策略',
    updateDetail: '梯度下降 + 优化器',
    increase: '提高正优势轨迹中选择的概率',
    decrease: '降低负优势轨迹中选择的概率',
    nextStep: '更新后的策略 → 下一 step',
    stepSummary: '一个 step：rollout → 验证 → 相对优势 → 参数更新 → 重复',
  },
  'zh-TW': {
    title: '一個 GRPO step：同一 SWE-bench 任務的 16 次 rollout',
    example: '章節中的假設範例',
    taskHeading: '同一任務 + 初始程式碼',
    taskBug: 'parser.py：空輸入觸發 IndexError',
    taskConstraint: 'Agent 不能修改測試',
    policyHeading: '目前策略模型',
    policyDetail: '獨立取樣 16 次',
    rolloutsHeading: '1 · 16 個隔離的 rollout',
    rolloutsDetail: '初始狀態相同 · 取樣路徑不同',
    pass: '通過',
    fail: '失敗',
    summary: '假設 4 條通過 · 12 條失敗',
    rewardHeading: '2 · 驗證並計算獎勵',
    rewardDetail: '在乾淨環境套用每個補丁，執行測試並檢查規則',
    rewardPass: '全部測試通過且未改測試 → 獎勵 1',
    rewardFail: '測試失敗或違規 → 獎勵 0',
    advantageHeading: '3 · 組內比較',
    advantageMean: '組內平均 = 4/16 = 0.25',
    advantagePass: '4 條通過：高於平均 → 正優勢',
    advantageFail: '12 條失敗：低於平均 → 負優勢',
    updateHeading: '4 · 更新策略',
    updateDetail: '梯度下降 + 最佳化器',
    increase: '提高正優勢軌跡中選擇的機率',
    decrease: '降低負優勢軌跡中選擇的機率',
    nextStep: '更新後的策略 → 下一 step',
    stepSummary: '一個 step：rollout → 驗證 → 相對優勢 → 參數更新 → 重複',
  },
  es: {
    title: 'Un step de GRPO: 16 rollouts de la misma tarea de SWE-bench',
    example: 'Ejemplo hipotético del capítulo',
    taskHeading: 'Misma tarea + código inicial',
    taskBug: 'parser.py: una entrada vacía provoca IndexError',
    taskConstraint: 'El Agent no debe modificar las pruebas',
    policyHeading: 'Modelo de política actual',
    policyDetail: 'Muestrea 16 intentos independientes',
    rolloutsHeading: '1 · 16 rollouts aislados',
    rolloutsDetail: 'Mismo estado inicial · rutas estocásticas',
    pass: 'pasa',
    fail: 'falla',
    summary: 'Supongamos: 4 pasan · 12 fallan',
    rewardHeading: '2 · Verificar y puntuar',
    rewardDetail:
      'Aplicar cada parche en un entorno limpio; ejecutar pruebas y comprobar reglas',
    rewardPass: 'Pasa todas las pruebas sin cambiarlas → recompensa 1',
    rewardFail: 'Pruebas fallidas o infracción → recompensa 0',
    advantageHeading: '3 · Comparar dentro del grupo',
    advantageMean: 'Media del grupo = 4/16 = 0,25',
    advantagePass: '4 rollouts aprobados: sobre la media → ventaja positiva',
    advantageFail: '12 rollouts fallidos: bajo la media → ventaja negativa',
    updateHeading: '4 · Actualizar la política',
    updateDetail: 'Descenso de gradiente + optimizador',
    increase: 'Aumentar elecciones de trayectorias con ventaja positiva',
    decrease: 'Reducir elecciones de trayectorias con ventaja negativa',
    nextStep: 'Política actualizada → siguiente step',
    stepSummary:
      'Un step: rollout → verificación → ventaja relativa → actualización → repetir',
  },
  id: {
    title: 'Satu step GRPO: 16 rollout untuk tugas SWE-bench yang sama',
    example: 'Contoh hipotetis dalam bab',
    taskHeading: 'Tugas sama + kode awal',
    taskBug: 'parser.py: masukan kosong memicu IndexError',
    taskConstraint: 'Agent tidak boleh mengubah pengujian',
    policyHeading: 'Model kebijakan saat ini',
    policyDetail: 'Mengambil 16 sampel independen',
    rolloutsHeading: '1 · 16 rollout terisolasi',
    rolloutsDetail: 'Keadaan awal sama · jalur stokastik',
    pass: 'lulus',
    fail: 'gagal',
    summary: 'Asumsikan 4 lulus · 12 gagal',
    rewardHeading: '2 · Verifikasi dan beri skor',
    rewardDetail:
      'Terapkan tiap patch di lingkungan bersih; jalankan pengujian dan periksa aturan',
    rewardPass: 'Semua pengujian lulus; pengujian tidak diubah → reward 1',
    rewardFail: 'Pengujian gagal atau aturan dilanggar → reward 0',
    advantageHeading: '3 · Bandingkan dalam kelompok',
    advantageMean: 'Rata-rata kelompok = 4/16 = 0,25',
    advantagePass: '4 rollout lulus: di atas rata-rata → advantage positif',
    advantageFail: '12 rollout gagal: di bawah rata-rata → advantage negatif',
    updateHeading: '4 · Perbarui kebijakan',
    updateDetail: 'Gradient descent + optimizer',
    increase: 'Naikkan peluang pilihan dari lintasan advantage positif',
    decrease: 'Turunkan peluang pilihan dari lintasan advantage negatif',
    nextStep: 'Kebijakan baru → step berikutnya',
    stepSummary:
      'Satu step: rollout → verifikasi → advantage relatif → pembaruan → ulangi',
  },
  ru: {
    title: 'Один step GRPO: 16 rollout одной задачи SWE-bench',
    example: 'Гипотетический пример из главы',
    taskHeading: 'Одна задача + исходный код',
    taskBug: 'parser.py: пустой ввод вызывает IndexError',
    taskConstraint: 'Agent не должен менять тесты',
    policyHeading: 'Текущая модель политики',
    policyDetail: 'Независимо создаёт 16 попыток',
    rolloutsHeading: '1 · 16 изолированных rollout',
    rolloutsDetail: 'Одинаковое начало · случайные траектории',
    pass: 'успех',
    fail: 'сбой',
    summary: 'Допустим: 4 успешных · 12 неудачных',
    rewardHeading: '2 · Проверка и награда',
    rewardDetail:
      'Применить каждый патч в чистой среде, запустить тесты и проверить правила',
    rewardPass: 'Все тесты пройдены и не изменены → награда 1',
    rewardFail: 'Тесты не пройдены или правило нарушено → награда 0',
    advantageHeading: '3 · Сравнение внутри группы',
    advantageMean: 'Среднее группы = 4/16 = 0,25',
    advantagePass: '4 успеха: выше среднего → положительное преимущество',
    advantageFail: '12 неудач: ниже среднего → отрицательное преимущество',
    updateHeading: '4 · Обновление политики',
    updateDetail: 'Градиентный спуск + оптимизатор',
    increase: 'Повысить вероятность выбора из траекторий с плюсом',
    decrease: 'Снизить вероятность выбора из траекторий с минусом',
    nextStep: 'Обновлённая политика → следующий step',
    stepSummary:
      'Один step: rollout → проверка → относительное преимущество → обновление → повтор',
  },
  ta: {
    title: 'ஒரு GRPO step: ஒரே SWE-bench பணியின் 16 rollout-கள்',
    example: 'அத்தியாயத்தின் கற்பனை எடுத்துக்காட்டு',
    taskHeading: 'ஒரே பணி + தொடக்கக் குறியீடு',
    taskBug: 'parser.py: வெற்று உள்ளீடு IndexError-ஐ ஏற்படுத்தும்',
    taskConstraint: 'Agent சோதனைகளை மாற்றக் கூடாது',
    policyHeading: 'தற்போதைய கொள்கை மாதிரி',
    policyDetail: '16 சுயாதீன முயற்சிகளை மாதிரியாக்கும்',
    rolloutsHeading: '1 · தனிமைப்படுத்தப்பட்ட 16 rollout-கள்',
    rolloutsDetail: 'ஒரே தொடக்க நிலை · சீரற்ற பாதைகள்',
    pass: 'தேர்ச்சி',
    fail: 'தோல்வி',
    summary: '4 தேர்ச்சி · 12 தோல்வி எனக் கொள்வோம்',
    rewardHeading: '2 · சரிபார்த்து வெகுமதி அளித்தல்',
    rewardDetail:
      'ஒவ்வொரு patch-ஐயும் தூய சூழலில் இட்டு, சோதனைகளையும் விதிகளையும் சரிபார்க்கவும்',
    rewardPass: 'அனைத்து சோதனைகளும் தேர்ச்சி; சோதனைகள் மாறவில்லை → வெகுமதி 1',
    rewardFail: 'சோதனைத் தோல்வி அல்லது விதிமீறல் → வெகுமதி 0',
    advantageHeading: '3 · குழுவுக்குள் ஒப்பிடுதல்',
    advantageMean: 'குழுச் சராசரி = 4/16 = 0.25',
    advantagePass: '4 தேர்ச்சி: சராசரிக்கு மேல் → நேர்மறை advantage',
    advantageFail: '12 தோல்வி: சராசரிக்குக் கீழ் → எதிர்மறை advantage',
    updateHeading: '4 · கொள்கையைப் புதுப்பித்தல்',
    updateDetail: 'Gradient descent + optimizer',
    increase: 'நேர்மறை-advantage பாதைத் தேர்வுகளின் நிகழ்தகவை உயர்த்தவும்',
    decrease: 'எதிர்மறை-advantage பாதைத் தேர்வுகளின் நிகழ்தகவை குறைக்கவும்',
    nextStep: 'புதுப்பித்த கொள்கை → அடுத்த step',
    stepSummary:
      'ஒரு step: rollout → சரிபார்ப்பு → relative advantage → புதுப்பிப்பு → மீண்டும்',
  },
  vi: {
    title: 'Một step GRPO: 16 rollout của cùng một tác vụ SWE-bench',
    example: 'Ví dụ giả định trong chương',
    taskHeading: 'Cùng tác vụ + mã ban đầu',
    taskBug: 'parser.py: đầu vào rỗng gây ra IndexError',
    taskConstraint: 'Agent không được sửa bài kiểm thử',
    policyHeading: 'Mô hình chính sách hiện tại',
    policyDetail: 'Lấy mẫu 16 lần thử độc lập',
    rolloutsHeading: '1 · 16 rollout cách ly',
    rolloutsDetail: 'Cùng trạng thái đầu · đường đi ngẫu nhiên',
    pass: 'đạt',
    fail: 'trượt',
    summary: 'Giả sử 4 đạt · 12 trượt',
    rewardHeading: '2 · Kiểm chứng và tính thưởng',
    rewardDetail:
      'Áp từng bản vá trong môi trường sạch; chạy kiểm thử và kiểm tra quy tắc',
    rewardPass: 'Qua mọi kiểm thử và không sửa kiểm thử → thưởng 1',
    rewardFail: 'Trượt kiểm thử hoặc vi phạm quy tắc → thưởng 0',
    advantageHeading: '3 · So sánh trong nhóm',
    advantageMean: 'Trung bình nhóm = 4/16 = 0,25',
    advantagePass: '4 rollout đạt: trên trung bình → lợi thế dương',
    advantageFail: '12 rollout trượt: dưới trung bình → lợi thế âm',
    updateHeading: '4 · Cập nhật chính sách',
    updateDetail: 'Hạ gradient + bộ tối ưu',
    increase: 'Tăng xác suất lựa chọn từ quỹ đạo có lợi thế dương',
    decrease: 'Giảm xác suất lựa chọn từ quỹ đạo có lợi thế âm',
    nextStep: 'Chính sách đã cập nhật → step tiếp theo',
    stepSummary:
      'Một step: rollout → kiểm chứng → lợi thế tương đối → cập nhật → lặp lại',
  },
  ja: {
    title: 'GRPO の 1 step：同じ SWE-bench タスクを 16 回 rollout',
    example: '章内の仮定例',
    taskHeading: '同じタスク + 初期コード',
    taskBug: 'parser.py：空入力で IndexError が発生',
    taskConstraint: 'Agent はテストを変更しない',
    policyHeading: '現在の方策モデル',
    policyDetail: '16 回の試行を独立にサンプリング',
    rolloutsHeading: '1 · 隔離された 16 回の rollout',
    rolloutsDetail: '初期状態は同じ · 経路は確率的',
    pass: '成功',
    fail: '失敗',
    summary: '4 回成功 · 12 回失敗と仮定',
    rewardHeading: '2 · 検証して報酬を計算',
    rewardDetail: '各パッチをクリーンな環境に適用し、テストとルールを確認',
    rewardPass: '全テスト成功、テスト変更なし → 報酬 1',
    rewardFail: 'テスト失敗または違反 → 報酬 0',
    advantageHeading: '3 · グループ内で比較',
    advantageMean: 'グループ平均 = 4/16 = 0.25',
    advantagePass: '成功 4 回：平均より上 → 正の advantage',
    advantageFail: '失敗 12 回：平均より下 → 負の advantage',
    updateHeading: '4 · 方策を更新',
    updateDetail: '勾配降下 + オプティマイザ',
    increase: '正の advantage を持つ軌跡の選択確率を上げる',
    decrease: '負の advantage を持つ軌跡の選択確率を下げる',
    nextStep: '更新した方策 → 次の step',
    stepSummary:
      '1 step：rollout → 検証 → 相対 advantage → パラメータ更新 → 反復',
  },
  ko: {
    title: 'GRPO 한 step: 동일 SWE-bench 과제의 rollout 16회',
    example: '장의 가정 예시',
    taskHeading: '동일 과제 + 초기 코드',
    taskBug: 'parser.py: 빈 입력에서 IndexError 발생',
    taskConstraint: 'Agent는 테스트를 수정하면 안 됨',
    policyHeading: '현재 정책 모델',
    policyDetail: '16번의 시도를 독립적으로 샘플링',
    rolloutsHeading: '1 · 격리된 rollout 16회',
    rolloutsDetail: '초기 상태 동일 · 확률적 경로',
    pass: '통과',
    fail: '실패',
    summary: '4회 통과 · 12회 실패라고 가정',
    rewardHeading: '2 · 검증하고 보상 계산',
    rewardDetail: '깨끗한 환경에 각 패치를 적용하고 테스트와 규칙을 확인',
    rewardPass: '모든 테스트 통과, 테스트 변경 없음 → 보상 1',
    rewardFail: '테스트 실패 또는 규칙 위반 → 보상 0',
    advantageHeading: '3 · 그룹 내 비교',
    advantageMean: '그룹 평균 = 4/16 = 0.25',
    advantagePass: '통과 4회: 평균보다 높음 → 양의 advantage',
    advantageFail: '실패 12회: 평균보다 낮음 → 음의 advantage',
    updateHeading: '4 · 정책 업데이트',
    updateDetail: '경사 하강 + 옵티마이저',
    increase: '양의 advantage 궤적에서 선택한 확률을 높임',
    decrease: '음의 advantage 궤적에서 선택한 확률을 낮춤',
    nextStep: '업데이트된 정책 → 다음 step',
    stepSummary:
      '한 step: rollout → 검증 → 상대 advantage → 파라미터 업데이트 → 반복',
  },
  ar: {
    title: 'خطوة GRPO واحدة: ‏16 rollout للمهمة نفسها في SWE-bench',
    example: 'مثال افتراضي من الفصل',
    taskHeading: 'المهمة نفسها + الشفرة الأولية',
    taskBug: 'parser.py: الإدخال الفارغ يسبب IndexError',
    taskConstraint: 'يجب ألا يغيّر الـ Agent الاختبارات',
    policyHeading: 'نموذج السياسة الحالي',
    policyDetail: 'يأخذ 16 محاولة مستقلة',
    rolloutsHeading: '1 · ‏16 rollout معزولة',
    rolloutsDetail: 'الحالة الأولية نفسها · مسارات عشوائية',
    pass: 'نجاح',
    fail: 'فشل',
    summary: 'نفترض نجاح 4 · وفشل 12',
    rewardHeading: '2 · التحقق وحساب المكافأة',
    rewardDetail:
      'طبّق كل patch في بيئة نظيفة، ثم شغّل الاختبارات وافحص القواعد',
    rewardPass: 'نجاح كل الاختبارات دون تغييرها ← المكافأة 1',
    rewardFail: 'فشل الاختبار أو مخالفة القواعد ← المكافأة 0',
    advantageHeading: '3 · المقارنة داخل المجموعة',
    advantageMean: 'متوسط المجموعة = 4/16 = 0.25',
    advantagePass: '4 ناجحة: فوق المتوسط ← أفضلية موجبة',
    advantageFail: '12 فاشلة: تحت المتوسط ← أفضلية سالبة',
    updateHeading: '4 · تحديث السياسة',
    updateDetail: 'الانحدار المتدرج + المحسّن',
    increase: 'زيادة احتمال اختيارات المسارات ذات الأفضلية الموجبة',
    decrease: 'خفض احتمال اختيارات المسارات ذات الأفضلية السالبة',
    nextStep: 'السياسة المحدّثة ← الخطوة التالية',
    stepSummary:
      'خطوة واحدة: rollout ← تحقق ← أفضلية نسبية ← تحديث المعاملات ← تكرار',
  },
  tr: {
    title: 'Bir GRPO step: aynı SWE-bench görevinin 16 rollout’u',
    example: 'Bölümdeki varsayımsal örnek',
    taskHeading: 'Aynı görev + başlangıç kodu',
    taskBug: 'parser.py: boş girdi IndexError üretir',
    taskConstraint: 'Agent testleri değiştirmemeli',
    policyHeading: 'Güncel politika modeli',
    policyDetail: '16 bağımsız deneme örnekler',
    rolloutsHeading: '1 · Yalıtılmış 16 rollout',
    rolloutsDetail: 'Aynı başlangıç durumu · rastlantısal yollar',
    pass: 'başarılı',
    fail: 'başarısız',
    summary: '4 başarılı · 12 başarısız varsayalım',
    rewardHeading: '2 · Doğrula ve ödüllendir',
    rewardDetail:
      'Her yamayı temiz ortamda uygula; testleri çalıştır ve kuralları denetle',
    rewardPass: 'Tüm testler geçer, testler değişmez → ödül 1',
    rewardFail: 'Test başarısız veya kural ihlali → ödül 0',
    advantageHeading: '3 · Grup içinde karşılaştır',
    advantageMean: 'Grup ortalaması = 4/16 = 0,25',
    advantagePass: '4 başarılı: ortalamanın üstü → pozitif avantaj',
    advantageFail: '12 başarısız: ortalamanın altı → negatif avantaj',
    updateHeading: '4 · Politikayı güncelle',
    updateDetail: 'Gradyan inişi + eniyileyici',
    increase: 'Pozitif avantajlı yörüngelerdeki seçimleri artır',
    decrease: 'Negatif avantajlı yörüngelerdeki seçimleri azalt',
    nextStep: 'Güncel politika → sonraki step',
    stepSummary:
      'Bir step: rollout → doğrulama → göreli avantaj → parametre güncelleme → tekrar',
  },
  hu: {
    title: 'Egy GRPO-step: ugyanazon SWE-bench feladat 16 rolloutja',
    example: 'A fejezet feltételezett példája',
    taskHeading: 'Azonos feladat + kezdőkód',
    taskBug: 'parser.py: üres bemenetnél IndexError keletkezik',
    taskConstraint: 'Az Agent nem módosíthatja a teszteket',
    policyHeading: 'Aktuális policy modell',
    policyDetail: '16 független próbát mintavételez',
    rolloutsHeading: '1 · 16 elkülönített rollout',
    rolloutsDetail: 'Azonos kezdőállapot · véletlen utak',
    pass: 'siker',
    fail: 'kudarc',
    summary: 'Tegyük fel: 4 siker · 12 kudarc',
    rewardHeading: '2 · Ellenőrzés és jutalmazás',
    rewardDetail:
      'Minden patch tiszta környezetbe kerül; tesztfuttatás és szabályellenőrzés',
    rewardPass: 'Minden teszt sikeres és változatlan → jutalom 1',
    rewardFail: 'Tesztkudarc vagy szabálysértés → jutalom 0',
    advantageHeading: '3 · Csoporton belüli összevetés',
    advantageMean: 'Csoportátlag = 4/16 = 0,25',
    advantagePass: '4 siker: átlag felett → pozitív előny',
    advantageFail: '12 kudarc: átlag alatt → negatív előny',
    updateHeading: '4 · A policy frissítése',
    updateDetail: 'Gradienscsökkentés + optimalizáló',
    increase: 'Nő a pozitív előnyű trajektóriák választásainak esélye',
    decrease: 'Csökken a negatív előnyű trajektóriák választásainak esélye',
    nextStep: 'Frissített policy → következő step',
    stepSummary:
      'Egy step: rollout → ellenőrzés → relatív előny → paraméterfrissítés → ismétlés',
  },
  he: {
    title: 'צעד GRPO אחד: 16 rollouts של אותה משימת SWE-bench',
    example: 'דוגמה היפותטית מהפרק',
    taskHeading: 'אותה משימה + קוד התחלתי',
    taskBug: 'parser.py: קלט ריק גורם ל־IndexError',
    taskConstraint: 'אסור ל־Agent לשנות את הבדיקות',
    policyHeading: 'מודל המדיניות הנוכחי',
    policyDetail: 'דוגם 16 ניסיונות עצמאיים',
    rolloutsHeading: '1 · ‏16 rollouts מבודדים',
    rolloutsDetail: 'אותו מצב התחלתי · מסלולים אקראיים',
    pass: 'עבר',
    fail: 'נכשל',
    summary: 'נניח ש־4 עברו · 12 נכשלו',
    rewardHeading: '2 · אימות וחישוב תגמול',
    rewardDetail:
      'מחילים כל patch בסביבה נקייה, מריצים בדיקות ובודקים את הכללים',
    rewardPass: 'כל הבדיקות עברו ולא שונו ← תגמול 1',
    rewardFail: 'כשל בבדיקה או הפרת כלל ← תגמול 0',
    advantageHeading: '3 · השוואה בתוך הקבוצה',
    advantageMean: 'ממוצע הקבוצה = 4/16 = 0.25',
    advantagePass: '4 עברו: מעל הממוצע ← יתרון חיובי',
    advantageFail: '12 נכשלו: מתחת לממוצע ← יתרון שלילי',
    updateHeading: '4 · עדכון המדיניות',
    updateDetail: 'ירידת גרדיאנט + ממטב',
    increase: 'מגדילים את הסתברות הבחירות ממסלולים עם יתרון חיובי',
    decrease: 'מקטינים את הסתברות הבחירות ממסלולים עם יתרון שלילי',
    nextStep: 'מדיניות מעודכנת ← הצעד הבא',
    stepSummary: 'צעד אחד: rollout ← אימות ← יתרון יחסי ← עדכון פרמטרים ← חזרה',
  },
  'pt-BR': {
    title: 'Um step de GRPO: 16 rollouts da mesma tarefa do SWE-bench',
    example: 'Exemplo hipotético do capítulo',
    taskHeading: 'Mesma tarefa + código inicial',
    taskBug: 'parser.py: entrada vazia causa IndexError',
    taskConstraint: 'O Agent não pode alterar os testes',
    policyHeading: 'Modelo de política atual',
    policyDetail: 'Amostra 16 tentativas independentes',
    rolloutsHeading: '1 · 16 rollouts isolados',
    rolloutsDetail: 'Mesmo estado inicial · caminhos estocásticos',
    pass: 'passou',
    fail: 'falhou',
    summary: 'Suponha: 4 passaram · 12 falharam',
    rewardHeading: '2 · Verificar e pontuar',
    rewardDetail:
      'Aplicar cada patch em ambiente limpo; executar testes e conferir regras',
    rewardPass: 'Todos os testes passam e permanecem intactos → recompensa 1',
    rewardFail: 'Falha nos testes ou violação de regra → recompensa 0',
    advantageHeading: '3 · Comparar dentro do grupo',
    advantageMean: 'Média do grupo = 4/16 = 0,25',
    advantagePass: '4 rollouts aprovados: acima da média → vantagem positiva',
    advantageFail:
      '12 rollouts reprovados: abaixo da média → vantagem negativa',
    updateHeading: '4 · Atualizar a política',
    updateDetail: 'Descida do gradiente + otimizador',
    increase: 'Aumentar escolhas de trajetórias com vantagem positiva',
    decrease: 'Reduzir escolhas de trajetórias com vantagem negativa',
    nextStep: 'Política atualizada → próximo step',
    stepSummary:
      'Um step: rollout → verificação → vantagem relativa → atualização → repetir',
  },
};

const passRollouts = new Set([2, 7, 11, 16]);

const escapeXml = (value) =>
  value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');

function label(text, key, x, y, width, height, options = {}) {
  const {
    size = 17,
    weight = 400,
    align = 'center',
    muted = false,
    mono = false,
  } = options;
  return `<foreignObject data-i18n="${key}" x="${x}" y="${y}" width="${width}" height="${height}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:${align === 'center' ? 'center' : 'flex-start'};font-family:${mono ? "'Courier New',Courier,monospace" : "Arial,'Helvetica Neue',Helvetica,'PingFang SC','Microsoft YaHei',sans-serif"};font-size:${size}px;font-weight:${weight};line-height:1.3;color:${muted ? '#52627a' : '#203047'};overflow-wrap:anywhere;text-align:${align === 'center' ? 'center' : 'start'}"><div dir="auto" style="width:100%">${escapeXml(text)}</div></div>
  </foreignObject>`;
}

const card = (x, y, width, height, fill = '#edf2f8') =>
  `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="8" fill="${fill}" stroke="#7386a0" stroke-width="2"/>`;

const arrow = (x1, y1, x2, y2) =>
  `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#52627a" stroke-width="2.5" marker-end="url(#grpo-arrow)"/>`;

export function layoutGrpoRollouts(locale) {
  const t = translations[locale];
  if (!t)
    throw new Error(`Figure 8-13 has no localization for locale: ${locale}`);

  const rolloutCells = Array.from({ length: 16 }, (_, index) => {
    const number = index + 1;
    const passed = passRollouts.has(number);
    const column = index % 4;
    const row = Math.floor(index / 4);
    const x = 582 + column * 119;
    const y = 230 + row * 56;
    const outcome = passed ? 'pass' : 'fail';
    return `<g data-rollout="${number}" data-outcome="${outcome}">
      <rect x="${x}" y="${y}" width="109" height="48" rx="6" fill="${passed ? '#dcefe9' : '#f9e2e4'}" stroke="#7386a0" stroke-width="1.5"/>
      ${label(`#${String(number).padStart(2, '0')} ${passed ? '✓' : '×'} ${t[outcome]}`, `rollout-${number}`, x + 5, y + 2, 99, 44, { size: 14, weight: 700 })}
    </g>`;
  }).join('');

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 1080" width="1100" height="1080" role="img" aria-labelledby="grpo-title grpo-desc" data-locale="${locale}" style="background:#f7f9fc">
  <title id="grpo-title">${escapeXml(t.title)}</title>
  <desc id="grpo-desc">${escapeXml(t.stepSummary)}</desc>
  <defs>
    <marker id="grpo-arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L10 4L0 8Z" fill="#52627a"/></marker>
  </defs>

  ${label(t.title, 'title', 30, 18, 1040, 48, { size: 25, weight: 700 })}
  <rect x="405" y="70" width="290" height="54" rx="8" fill="#fff0cb" stroke="#7386a0" stroke-width="1.5"/>
  ${label(t.example, 'example', 418, 75, 264, 44, { size: 15, weight: 700 })}

  ${card(30, 145, 250, 245, '#ffffff')}
  ${label(t.taskHeading, 'taskHeading', 48, 157, 214, 50, { size: 19, weight: 700 })}
  ${label(t.taskBug, 'taskBug', 48, 214, 214, 82, { size: 15, mono: true, align: 'start' })}
  ${label(t.taskConstraint, 'taskConstraint', 48, 304, 214, 64, { size: 15, align: 'start', muted: true })}

  ${arrow(282, 267, 322, 267)}
  ${card(326, 170, 190, 190, '#dce7f5')}
  ${label(t.policyHeading, 'policyHeading', 344, 180, 154, 82, { size: 19, weight: 700 })}
  ${label(t.policyDetail, 'policyDetail', 344, 270, 154, 70, { size: 15, muted: true })}
  ${arrow(518, 267, 558, 267)}

  ${card(562, 140, 508, 350, '#ffffff')}
  ${label(t.rolloutsHeading, 'rolloutsHeading', 582, 148, 468, 38, { size: 20, weight: 700 })}
  ${label(t.rolloutsDetail, 'rolloutsDetail', 582, 188, 468, 32, { size: 14, muted: true })}
  ${rolloutCells}
  ${label(t.summary, 'summary', 582, 454, 468, 28, { size: 15, weight: 700 })}

  ${arrow(816, 492, 816, 526)}
  ${card(562, 530, 508, 220, '#edf2f8')}
  ${label(t.rewardHeading, 'rewardHeading', 582, 540, 468, 38, { size: 20, weight: 700 })}
  ${label(t.rewardDetail, 'rewardDetail', 582, 584, 468, 58, { size: 14, muted: true })}
  ${label(t.rewardPass, 'rewardPass', 582, 650, 226, 88, { size: 15, weight: 700 })}
  ${label(t.rewardFail, 'rewardFail', 824, 650, 226, 88, { size: 15, weight: 700 })}

  ${arrow(816, 752, 816, 790)}
  ${card(562, 794, 508, 156, '#ffffff')}
  ${label(t.advantageHeading, 'advantageHeading', 582, 802, 468, 38, { size: 20, weight: 700 })}
  ${label(t.advantageMean, 'advantageMean', 582, 841, 468, 30, { size: 16, weight: 700, mono: true })}
  ${label(t.advantagePass, 'advantagePass', 582, 878, 226, 60, { size: 15 })}
  ${label(t.advantageFail, 'advantageFail', 824, 878, 226, 60, { size: 15 })}

  ${arrow(560, 872, 522, 872)}
  ${card(104, 794, 416, 156, '#dce7f5')}
  ${label(t.updateHeading, 'updateHeading', 124, 802, 376, 38, { size: 20, weight: 700 })}
  ${label(t.updateDetail, 'updateDetail', 124, 841, 376, 30, { size: 16, weight: 700 })}
  ${label(`↑ ${t.increase}`, 'increase', 124, 878, 180, 60, { size: 14 })}
  ${label(`↓ ${t.decrease}`, 'decrease', 320, 878, 180, 60, { size: 14 })}

  <path d="M104 872H50V500H421V364" fill="none" stroke="#52627a" stroke-width="2.5" stroke-dasharray="8 6" marker-end="url(#grpo-arrow)"/>
  ${label(t.nextStep, 'nextStep', 64, 516, 350, 52, { size: 15, weight: 700, muted: true })}

  ${card(30, 978, 1040, 82, '#fff0cb')}
  ${label(t.stepSummary, 'stepSummary', 55, 990, 990, 58, { size: 18, weight: 700 })}
</svg>`;
}

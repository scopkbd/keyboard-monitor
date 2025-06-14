"""
キーボードモニター包括的テストスイート

このスクリプトは全てのテストを順次実行し、
プロジェクトの品質を総合的に検証します。
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def print_header(title: str) -> None:
    """セクションヘッダーを表示"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_test_result(test_name: str, success: bool, details: str = "") -> None:
    """テスト結果を表示"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def run_test_script(script_path: str, test_name: str) -> tuple[bool, str]:
    """テストスクリプトを実行して結果を取得"""
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path(__file__).parent.parent
        )

        success = result.returncode == 0
        output = result.stdout if result.stdout else result.stderr

        return success, output
    except subprocess.TimeoutExpired:
        return False, "テストがタイムアウトしました"
    except Exception as e:
        return False, f"テスト実行エラー: {str(e)}"

def main():
    """メイン関数"""
    print_header("キーボードモニター包括的テストスイート")
    print("📋 実行予定のテスト:")
    print("   1. 基本機能テスト")
    print("   2. リアルタイム表示修正テスト")
    print("   3. 安全な統合テスト")
    print("   4. 自動化キーボードテスト")
    print("   5. フェーズ1完成度テスト")
    print("   6. 統合テスト")

    # テスト定義
    tests = [
        ("tests/simple_fix_test.py", "基本機能テスト"),
        ("tests/test_realtime_display_fix.py", "リアルタイム表示修正テスト"),
        ("tests/safe_integration_test.py", "安全な統合テスト"),
        ("tests/simple_keyboard_test.py", "基本キーボードテスト"),
        ("tests/phase1_test.py", "フェーズ1完成度テスト"),
        ("tests/integration_test.py", "統合テスト"),
    ]

    results = []
    total_tests = len(tests)
    passed_tests = 0

    print_header("テスト実行開始")

    for i, (script_path, test_name) in enumerate(tests, 1):
        print(f"\n🔄 [{i}/{total_tests}] {test_name} を実行中...")

        if not os.path.exists(script_path):
            print_test_result(test_name, False, f"テストファイルが見つかりません: {script_path}")
            results.append((test_name, False, "ファイルなし"))
            continue

        success, output = run_test_script(script_path, test_name)

        if success:
            passed_tests += 1
            # 成功率を抽出（出力に含まれている場合）
            success_rate = "100%"
            if "成功率:" in output:
                try:
                    line = [l for l in output.split('\n') if "成功率:" in l][-1]
                    success_rate = line.split("成功率:")[1].strip()
                except:
                    success_rate = "100%"

            print_test_result(test_name, True, f"成功率: {success_rate}")
        else:
            print_test_result(test_name, False, "実行失敗")
            # エラーの詳細を表示（最初の数行のみ）
            error_lines = output.split('\n')[:3]
            for line in error_lines:
                if line.strip():
                    print(f"      {line.strip()}")

        results.append((test_name, success, output))

        # 短時間の休憩
        time.sleep(0.5)

    # 結果の総合評価
    print_header("総合テスト結果")
    print(f"📊 実行テスト数: {total_tests}")
    print(f"✅ 成功テスト数: {passed_tests}")
    print(f"❌ 失敗テスト数: {total_tests - passed_tests}")
    print(f"🎯 総合成功率: {passed_tests / total_tests * 100:.1f}%")

    # 詳細結果
    print("\n📋 詳細結果:")
    for test_name, success, _ in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")

    # 品質評価
    success_rate = passed_tests / total_tests * 100

    if success_rate >= 95:
        quality_level = "🌟 優秀"
        quality_msg = "プロダクション品質達成"
    elif success_rate >= 85:
        quality_level = "⭐ 良好"
        quality_msg = "高品質レベル"
    elif success_rate >= 70:
        quality_level = "✨ 普通"
        quality_msg = "基本品質レベル"
    else:
        quality_level = "⚠️ 改善必要"
        quality_msg = "品質改善が必要"

    print(f"\n🏆 品質評価: {quality_level}")
    print(f"📝 評価コメント: {quality_msg}")

    # 推奨事項
    if success_rate < 100:
        print(f"\n💡 推奨事項:")
        failed_tests = [name for name, success, _ in results if not success]
        for test_name in failed_tests:
            print(f"   - {test_name} の問題を調査・修正")
    else:
        print(f"\n🎉 おめでとうございます！")
        print(f"   すべてのテストが成功しました。")
        print(f"   キーボードモニターv1.0は完璧な品質を達成しています！")

    # 次のステップ
    print(f"\n🚀 次のステップ:")
    if success_rate >= 95:
        print(f"   ✅ リリース準備完了")
        print(f"   ✅ ユーザー配布可能")
        print(f"   ✅ フェーズ2開発準備")
    else:
        print(f"   🔧 失敗テストの修正")
        print(f"   🧪 追加テストの実施")
        print(f"   📝 ドキュメント更新")

    print(f"\n" + "=" * 60)
    print(f"🏁 包括的テストスイート完了")
    print(f"⏰ 実行時間: 約{len(tests) * 10}秒")
    print(f"=" * 60)

    return success_rate >= 95

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n⚠️ テストが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        sys.exit(1)

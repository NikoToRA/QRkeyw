"""Main module for QR2Key application."""

import sys
import os
import platform
import qrcode
import time
import serial
import serial.tools.list_ports
from PIL import Image
from cryptography.fernet import Fernet
from pynput.keyboard import Controller

if platform.system() == 'Windows':
    try:
        import win32clipboard
        import win32con
        WIN32_AVAILABLE = True
    except ImportError:
        print("Warning: pywin32 is not installed. Some features will be disabled.")
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False


def generate_key():
    """Generate a new cryptographic key."""
    return Fernet.generate_key()


def key_to_qr(key, output_path='key_qr.png'):
    """Convert a cryptographic key to a QR code image.
    
    Args:
        key: The cryptographic key as bytes
        output_path: Path to save the QR code image
        
    Returns:
        The path to the saved QR code image
    """
    key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(key_str)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    return output_path


def copy_to_clipboard(text):
    """Copy text to clipboard.
    
    On Windows, uses pywin32. On other platforms, prints a message.
    
    Args:
        text: The text to copy to clipboard
    """
    if WIN32_AVAILABLE:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        print("Text copied to clipboard.")
    else:
        print("Clipboard functionality is only available on Windows.")
        print(f"Text to copy: {text}")


def list_com_ports():
    """
    リスト内のすべての利用可能なCOMポートを一覧表示します。
    
    Returns:
        利用可能なCOMポートのリスト
    """
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("利用可能なCOMポートが見つかりません。")
        return []
    
    print("利用可能なCOMポート:")
    for i, port in enumerate(ports):
        print(f"{i+1}. {port.device} - {port.description}")
    
    return [port.device for port in ports]


def select_com_port():
    """
    ユーザーに使用するCOMポートを選択させます。
    
    Returns:
        選択されたCOMポート名、またはNone（キャンセルの場合）
    """
    ports = list_com_ports()
    if not ports:
        return None
    
    try:
        selection = input("\nCOMポート番号を入力してください（1～" + str(len(ports)) + "）、または'q'で終了: ")
        if selection.lower() == 'q':
            return None
        
        index = int(selection) - 1
        if 0 <= index < len(ports):
            return ports[index]
        else:
            print("無効な選択です。")
            return select_com_port()  # 再帰的に再試行
    except ValueError:
        print("数値を入力してください。")
        return select_com_port()  # 再帰的に再試行


def read_qr_from_com_port(port, baudrate=9600, timeout=1.0):
    """
    指定されたCOMポートからQRコードデータを読み取ります。
    データはShift_JISエンコードされていると想定します。
    
    Args:
        port: COMポート名（例：'COM3'）
        baudrate: ボーレート
        timeout: 読み取りタイムアウト（秒）
        
    Returns:
        読み取られたデータを文字列として返します。エラーの場合はNoneを返します。
    """
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"{port}を開きました。QRコードをスキャンしてください...")
        
        data = ser.readline()
        if data:
            # Shift_JISでデコード
            try:
                decoded_data = data.decode('shift_jis', errors='replace').strip()
                print(f"データを受信しました（{len(decoded_data)}文字）")
                return decoded_data
            except UnicodeDecodeError:
                print("Shift_JISデコードエラー。他のエンコーディングを試します...")
                try:
                    # フォールバックとしてUTF-8を試す
                    decoded_data = data.decode('utf-8', errors='replace').strip()
                    print(f"UTF-8でデコードしました（{len(decoded_data)}文字）")
                    return decoded_data
                except:
                    print("デコードエラー。データを処理できません。")
                    return None
        else:
            print("データを受信できませんでした。")
            return None
        
    except serial.SerialException as e:
        print(f"COMポートエラー: {e}")
        return None
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print(f"{port}を閉じました。")


def simulate_keyboard_input(text):
    """
    指定されたテキストをキーボード入力としてシミュレートします。
    
    Args:
        text: 入力するテキスト
    """
    if not text:
        print("入力するテキストがありません。")
        return
    
    print(f"入力準備中: {len(text)}文字")
    print("3秒以内にテキスト入力欄にカーソルを合わせてください...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    keyboard = Controller()
    try:
        print("入力中...")
        keyboard.type(text)
        print("入力完了しました。")
    except Exception as e:
        print(f"キーボード入力エラー: {e}")


def main():
    """
    QR2Keyメインアプリケーション関数
    """
    print("QR2Key - QRコードからキーボード入力ツール")
    print("==========================================")
    
    # COMポート選択
    port = select_com_port()
    if not port:
        print("操作をキャンセルしました。")
        return
    
    while True:
        print("\nオプションを選択してください:")
        print("1. QRコードを読み取ってキーボード入力する")
        print("2. COMポートを変更する")
        print("q. 終了")
        
        choice = input("選択: ").strip().lower()
        
        if choice == '1':
            # QRコード読み取りとキーボード入力
            qr_data = read_qr_from_com_port(port)
            if qr_data:
                simulate_keyboard_input(qr_data)
        
        elif choice == '2':
            # COMポート変更
            new_port = select_com_port()
            if new_port:
                port = new_port
                print(f"COMポートを {port} に変更しました。")
        
        elif choice == 'q':
            print("QR2Keyを終了します。")
            break
        
        else:
            print("無効な選択です。もう一度試してください。")


# 開発・テスト用関数
def test_com_port_reading(port='COM3', baudrate=9600, timeout=1):
    """
    指定されたCOMポートからのデータ読み取りをテストします。
    """
    print(f"COMポート {port} を開こうとしています...")
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"{port} を開きました。")
        print("データ受信中... (Ctrl+Cで停止)")
        while True:
            try:
                data = ser.readline()
                if data:
                    # ASCII、UTF-8、Shift_JISでのデコードを試みる
                    print("受信データ (16進数):", data.hex())
                    try:
                        ascii_text = data.decode('ascii', errors='replace').strip()
                        print(f"ASCII: {ascii_text}")
                    except:
                        pass
                    
                    try:
                        utf8_text = data.decode('utf-8', errors='replace').strip()
                        print(f"UTF-8: {utf8_text}")
                    except:
                        pass
                    
                    try:
                        sjis_text = data.decode('shift_jis', errors='replace').strip()
                        print(f"Shift_JIS: {sjis_text}")
                    except:
                        pass
                    
                    print("-" * 30)
                
                # データが無い場合のCPU使用率を下げるための小さな遅延
                time.sleep(0.1)
            except serial.SerialException as e:
                print(f"COMポートからの読み取りエラー: {e}")
                break
            except KeyboardInterrupt:
                print("COMポートリスナーを停止します。")
                break
        ser.close()
        print(f"{port} を閉じました。")
    except serial.SerialException as e:
        print(f"COMポート {port} を開くまたは使用中にエラー: {e}")
        print("COMポートが正しく、利用可能であり、デバイスが接続されていることを確認してください。")


def test_keyboard_simulation(text_to_type="テスト入力 ABC 123"):
    """
    事前定義された文字列の入力をシミュレートします。
    """
    print(f"入力準備中: '{text_to_type}'") 
    print("5秒以内にテキスト入力欄にカーソルを合わせてください...")
    time.sleep(5) # ユーザーがテキストフィールドにフォーカスするための時間

    keyboard = Controller()
    try:
        print("入力中...")
        keyboard.type(text_to_type)
        print("入力完了。")
    except Exception as e:
        print(f"キーボードシミュレーション中のエラー: {e}")


if __name__ == "__main__":
    # コマンドライン引数によるモード選択
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("QR2Key - テストモード")
        print("====================")
        print("\n1. COMポート読み取りテスト")
        print("2. キーボード入力テスト")
        print("q. 終了")
        
        choice = input("\n選択: ").strip().lower()
        
        if choice == '1':
            # COMポートテスト
            ports = list_com_ports()
            if ports:
                port_choice = input("テストするCOMポート番号を入力してください: ")
                try:
                    port_index = int(port_choice) - 1
                    if 0 <= port_index < len(ports):
                        test_com_port_reading(port=ports[port_index])
                    else:
                        print("無効な選択です。")
                except ValueError:
                    print("数値を入力してください。")
            else:
                print("利用可能なCOMポートがありません。")
        
        elif choice == '2':
            # キーボードテスト
            test_text = input("入力するテキストを入力してください (デフォルト: 'テスト入力 ABC 123'): ")
            if not test_text:
                test_text = "テスト入力 ABC 123"
            test_keyboard_simulation(test_text)
        
        elif choice == 'q':
            print("テストモードを終了します。")
    else:
        # 通常モード - メインアプリケーション実行
        main()

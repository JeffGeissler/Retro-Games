"""Optional system TTS renderer. Its blocking engine loop lives only in this child."""
import sys


def main():
    import pyttsx3
    text = sys.stdin.read(601)
    if len(text) > 600:
        raise ValueError('Speech text too long')
    engine = pyttsx3.init()
    engine.setProperty('rate', 145)
    engine.setProperty('volume', 1.0)
    engine.save_to_file(text, sys.argv[1])
    engine.runAndWait()
    engine.stop()


if __name__ == '__main__':
    main()

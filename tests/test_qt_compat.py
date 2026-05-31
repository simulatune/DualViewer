import unittest

from core.qt_compat import configure_qt_environment


class QtCompatTests(unittest.TestCase):

    def test_linux_wayland_with_xwayland_forces_xcb_by_default(self):
        env = {
            "WAYLAND_DISPLAY": "wayland-0",
            "DISPLAY": ":0",
            "LANG": "zh_CN.UTF-8",
        }

        actions = configure_qt_environment(env, platform="linux")

        self.assertEqual(env["QT_QPA_PLATFORM"], "xcb")
        self.assertEqual(env["QT_MEDIA_BACKEND"], "ffmpeg")
        self.assertEqual(env["QT_DISABLE_HW_TEXTURES_CONVERSION"], "1")
        self.assertEqual(env["QT_FFMPEG_DECODING_HW_DEVICE_TYPES"], ",")
        self.assertIn("prefer_xwayland", actions)
        self.assertIn("media_backend_ffmpeg", actions)
        self.assertIn("disable_hw_texture_conversion", actions)
        self.assertIn("disable_hw_decoding", actions)

    def test_linux_wayland_without_display_keeps_wayland_fallback(self):
        env = {
            "WAYLAND_DISPLAY": "wayland-0",
            "LANG": "zh_CN.UTF-8",
        }

        actions = configure_qt_environment(env, platform="linux")

        self.assertEqual(env["QT_QPA_PLATFORM"], "xcb;wayland")
        self.assertIn("prefer_xwayland", actions)

    def test_existing_qt_platform_is_not_overridden(self):
        env = {
            "WAYLAND_DISPLAY": "wayland-0",
            "LANG": "zh_CN.UTF-8",
            "QT_QPA_PLATFORM": "wayland",
        }

        actions = configure_qt_environment(env, platform="linux")

        self.assertEqual(env["QT_QPA_PLATFORM"], "wayland")
        self.assertNotIn("prefer_xwayland", actions)
        self.assertIn("disable_hw_texture_conversion", actions)

    def test_native_wayland_switch_skips_xwayland_preference(self):
        env = {
            "WAYLAND_DISPLAY": "wayland-0",
            "LANG": "zh_CN.UTF-8",
            "DUALVIEWER_NATIVE_WAYLAND": "1",
        }

        actions = configure_qt_environment(env, platform="linux")

        self.assertNotIn("QT_QPA_PLATFORM", env)
        self.assertNotIn("prefer_xwayland", actions)
        self.assertEqual(env["QT_DISABLE_HW_TEXTURES_CONVERSION"], "1")
        self.assertEqual(env["QT_FFMPEG_DECODING_HW_DEVICE_TYPES"], ",")

    def test_hardware_video_switch_preserves_gpu_video_path(self):
        env = {
            "WAYLAND_DISPLAY": "wayland-0",
            "LANG": "zh_CN.UTF-8",
            "DUALVIEWER_ENABLE_HW_VIDEO": "1",
        }

        actions = configure_qt_environment(env, platform="linux")

        self.assertNotIn("QT_DISABLE_HW_TEXTURES_CONVERSION", env)
        self.assertNotIn("QT_FFMPEG_DECODING_HW_DEVICE_TYPES", env)
        self.assertNotIn("disable_hw_texture_conversion", actions)
        self.assertNotIn("disable_hw_decoding", actions)

    def test_existing_media_and_video_settings_are_not_overridden(self):
        env = {
            "WAYLAND_DISPLAY": "wayland-0",
            "LANG": "zh_CN.UTF-8",
            "QT_MEDIA_BACKEND": "gstreamer",
            "QT_DISABLE_HW_TEXTURES_CONVERSION": "0",
            "QT_FFMPEG_DECODING_HW_DEVICE_TYPES": "vaapi",
        }

        actions = configure_qt_environment(env, platform="linux")

        self.assertEqual(env["QT_MEDIA_BACKEND"], "gstreamer")
        self.assertEqual(env["QT_DISABLE_HW_TEXTURES_CONVERSION"], "0")
        self.assertEqual(env["QT_FFMPEG_DECODING_HW_DEVICE_TYPES"], "vaapi")
        self.assertNotIn("media_backend_ffmpeg", actions)
        self.assertNotIn("disable_hw_texture_conversion", actions)
        self.assertNotIn("disable_hw_decoding", actions)

    def test_linux_without_locale_gets_utf8_locale(self):
        env = {}

        actions = configure_qt_environment(env, platform="linux")

        self.assertEqual(env["LC_ALL"], "C.UTF-8")
        self.assertEqual(env["QT_MEDIA_BACKEND"], "ffmpeg")
        self.assertIn("locale", actions)
        self.assertIn("media_backend_ffmpeg", actions)

    def test_non_linux_is_left_untouched(self):
        env = {"WAYLAND_DISPLAY": "wayland-0"}

        actions = configure_qt_environment(env, platform="darwin")

        self.assertEqual(env, {"WAYLAND_DISPLAY": "wayland-0"})
        self.assertEqual(actions, [])


if __name__ == "__main__":
    unittest.main()

// Download Apple's on-demand fonts so CI-built PDFs match local builds.
//
// Since macOS Sequoia, PingFang (and other CJK fonts) are no longer preinstalled
// in /System/Library/Fonts; they live in on-demand asset bundles that a fresh
// GitHub runner has never downloaded. Without this step, rsvg-convert falls back
// to Hiragino Sans (a Japanese font) for Chinese text in SVG figures.
//
// Usage: swift download_apple_fonts.swift "PingFang SC" "PingFang TC"
// Exits non-zero if any requested family is still unavailable afterwards.

import CoreText
import Foundation

let families = Array(CommandLine.arguments.dropFirst())
guard !families.isEmpty else {
    fputs("usage: download_apple_fonts.swift <family name>...\n", stderr)
    exit(2)
}

func isAvailable(_ family: String) -> Bool {
    let attrs = [kCTFontFamilyNameAttribute: family] as CFDictionary
    let desc = CTFontDescriptorCreateWithAttributes(attrs)
    // CoreText falls back to a default font when the family is missing, so
    // confirm the resolved font really has the requested family name.
    let font = CTFontCreateWithFontDescriptor(desc, 12, nil)
    guard CTFontCopyFamilyName(font) as String == family else { return false }
    // CoreText registers on-demand fonts (dimmed in Font Book) before they are
    // downloaded; the family name then matches but there is no font file yet,
    // and renderers quietly substitute another font. Require a real file.
    guard let url = CTFontCopyAttribute(font, kCTFontURLAttribute) as? URL else {
        print("\(family): registered but no font file on disk")
        return false
    }
    return FileManager.default.fileExists(atPath: url.path)
}

var failed = false
for family in families {
    if isAvailable(family) {
        print("\(family): already available")
        continue
    }
    print("\(family): not available, requesting download...")
    let attrs = [kCTFontFamilyNameAttribute: family] as CFDictionary
    let desc = CTFontDescriptorCreateWithAttributes(attrs)
    let sema = DispatchSemaphore(value: 0)
    var lastError: CFError?
    CTFontDescriptorMatchFontDescriptorsWithProgressHandler([desc] as CFArray, nil) { state, progress in
        switch state {
        case .didFailWithError:
            let params = progress as NSDictionary
            lastError = (params[kCTFontDescriptorMatchingError] as! CFError)
            sema.signal()
        case .didFinish:
            sema.signal()
        default:
            break
        }
        return true
    }
    if sema.wait(timeout: .now() + 300) == .timedOut {
        print("\(family): download timed out")
        failed = true
        continue
    }
    if let err = lastError {
        print("\(family): download failed: \(err)")
        failed = true
        continue
    }
    if isAvailable(family) {
        print("\(family): downloaded successfully")
    } else {
        print("\(family): still unavailable after download attempt")
        failed = true
    }
}
exit(failed ? 1 : 0)

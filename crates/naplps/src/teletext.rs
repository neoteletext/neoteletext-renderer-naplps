//! NeoTeletext's teletext character sets as NAPLPS private sets (REQ-6668, DEC-6677).
//!
//! ANSI X3.110-1983 section 4.3.2 allows "other G- ... sets defined according to the rules of
//! ISO 2022-1982", and ISO 2022 reserves the final bytes of column 3 for private sets (ECMA-35
//! sixth edition, which is ISO/IEC 2022:1994, section 13.3.3), from a separate series for each
//! type of set (section 14.1 note 44), with a second intermediate 2/1 to 2/3 to supplement the
//! final byte (section 13.2.2, Table 3.b). Set number n is the engine's `FONT_SETS` place n; its
//! final byte is 3/(n mod 16), after a second intermediate 2/(n div 16) when n is 16 or more.
//! With the first intermediate 2/8 to 2/11 a set is designated as a 94-character set into G0 to
//! G3, with 2/13 to 2/15 as a 96-character set into G1 to G3 (section 14.3.2, Table 6).
//!
//! These sets are the only means of text in another script (the owner's ruling DEC-6669): the
//! glyphs come from the caller as [`crate::BitmapSet`]s made from the project's own Noto
//! Teletext fonts, never from the page.

/// The number of NeoTeletext's character sets: the engine's `FONT_SET_COUNT`, EN 300 706's 24
/// and NeoTeletext's own 31.
pub const TELETEXT_SET_COUNT: usize = 55;

/// The names of the sets, in number order: the engine's `FONT_SETS` names
/// (`crates/neoteletext-core/src/glyphs/conformance.rs`), which `naplps-render`'s tests check
/// against the engine's checkout.
pub const TELETEXT_SETS: [&str; TELETEXT_SET_COUNT] = [
    "G0-Latin",
    "G0-Latin-English",
    "G0-Latin-German",
    "G0-Latin-SwedishFinnishHungarian",
    "G0-Latin-Italian",
    "G0-Latin-French",
    "G0-Latin-PortugueseSpanish",
    "G0-Latin-CzechSlovak",
    "G0-Latin-Polish",
    "G0-Latin-Turkish",
    "G0-Latin-SerbianCroatianSlovenian",
    "G0-Latin-Rumanian",
    "G0-Latin-Estonian",
    "G0-Latin-LettishLithuanian",
    "G0-Cyrillic-1",
    "G0-Cyrillic-2",
    "G0-Cyrillic-3",
    "G0-Greek",
    "G0-Arabic",
    "G0-Hebrew",
    "G2-Latin",
    "G2-Cyrillic",
    "G2-Greek",
    "G2-Arabic",
    "G0-Latin-HausaFula",
    "G0-Latin-WestAfrican",
    "G0-Latin-Ewe",
    "G0-Latin-KabyleTamazight",
    "G0-Latin-Azerbaijani",
    "G0-Latin-KanuriMossi",
    "G0-Vietnamese",
    "G0-Igbo",
    "G0-Cyrillic-Ukrainian",
    "G0-Cyrillic-Belarusian",
    "G0-Cyrillic-Macedonian",
    "G0-Cyrillic-Serbian",
    "G0-Cyrillic-KyrgyzMongolian",
    "G0-Cyrillic-Tatar",
    "G0-Cyrillic-Tajik",
    "G0-Georgian",
    "G0-Armenian",
    "G0-Tifinagh",
    "G2-Vietnamese",
    "G2-Armenian",
    "G0-Arabic-Persian",
    "G0-Arabic-Urdu",
    "G0-Arabic-Pashto",
    "G0-Arabic-Sindhi",
    "G0-Arabic-Sorani",
    "G0-Arabic-Uyghur",
    "G0-Arabic-Balochi",
    "G0-Arabic-Plain",
    "G0-Latin-JapaneseRomaji",
    "G0-Hiragana",
    "G0-Katakana",
];

/// The first private final byte, 3/0 (ECMA-35 section 13.3.3: column 3).
const FIRST_PRIVATE_FINAL: u8 = 0x30;
/// The last private final byte, 3/15.
const LAST_PRIVATE_FINAL: u8 = 0x3F;
/// Private sets one series of final bytes names: the sixteen of column 3.
const FINALS_PER_SERIES: u8 = LAST_PRIVATE_FINAL - FIRST_PRIVATE_FINAL + 1;
/// The supplementing second intermediates, 2/1 to 2/3 (ECMA-35 Table 3.b, "Use" R).
const FIRST_SUPPLEMENT: u8 = 0x21;
/// See [`FIRST_SUPPLEMENT`].
const LAST_SUPPLEMENT: u8 = 0x23;
/// The intermediate of a multiple-byte designation, 2/4 (ECMA-35 section 14.3.2, Table 6).
pub(crate) const MULTIPLE_BYTE: u8 = 0x24;

// Four series (no supplement, 2/1, 2/2, 2/3) of sixteen hold every set.
const _: () =
    assert!(TELETEXT_SET_COUNT <= FINALS_PER_SERIES as usize * (LAST_SUPPLEMENT - FIRST_SUPPLEMENT + 2) as usize);

/// Whether `byte` is a private final byte (column 3).
pub(crate) const fn is_private_final(byte: u8) -> bool {
    byte >= FIRST_PRIVATE_FINAL && byte <= LAST_PRIVATE_FINAL
}

/// The NeoTeletext set a private designation names: the intermediates after the first (the
/// slot's) and the final byte. `None` for every private designation that is not one of the
/// sets, which designates the null set (section 4.3.2): a number past the last set, a
/// supplement other than 2/1 to 2/3 (2/0 is the SELECT-DRCS indicator, ECMA-35 section 14.4,
/// and these sets are not DRCS), or more than one further intermediate.
pub(crate) fn private_set_number(further: &[u8], final_byte: u8) -> Option<u8> {
    if !is_private_final(final_byte) {
        return None;
    }
    let series = match further {
        [] => 0,
        [supplement] if (FIRST_SUPPLEMENT..=LAST_SUPPLEMENT).contains(supplement) => {
            supplement.checked_sub(FIRST_SUPPLEMENT)?.checked_add(1)?
        }
        _ => return None,
    };
    let number = series.checked_mul(FINALS_PER_SERIES)?.checked_add(final_byte.checked_sub(FIRST_PRIVATE_FINAL)?)?;
    (usize::from(number) < TELETEXT_SET_COUNT).then_some(number)
}

/// The final byte and the further intermediates (none, or one supplement) that designate set
/// `number`, for a caller writing a page; `None` past the last set.
#[must_use]
pub fn designation_of(number: u8) -> Option<(Option<u8>, u8)> {
    if usize::from(number) >= TELETEXT_SET_COUNT {
        return None;
    }
    let series = number.checked_div(FINALS_PER_SERIES)?;
    let final_byte = FIRST_PRIVATE_FINAL.checked_add(number.checked_rem(FINALS_PER_SERIES)?)?;
    let supplement = if series == 0 { None } else { Some(FIRST_SUPPLEMENT.checked_add(series.checked_sub(1)?)?) };
    Some((supplement, final_byte))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_set_round_trips_through_its_designation() {
        for number in 0..u8::try_from(TELETEXT_SET_COUNT).unwrap() {
            let (supplement, final_byte) = designation_of(number).unwrap();
            let further: &[u8] = match &supplement {
                Some(byte) => core::slice::from_ref(byte),
                None => &[],
            };
            assert_eq!(private_set_number(further, final_byte), Some(number));
        }
    }

    #[test]
    fn the_table_of_req_6668() {
        assert_eq!(designation_of(0), Some((None, 0x30)));
        assert_eq!(designation_of(15), Some((None, 0x3F)));
        assert_eq!(designation_of(16), Some((Some(0x21), 0x30)));
        assert_eq!(designation_of(31), Some((Some(0x21), 0x3F)));
        assert_eq!(designation_of(32), Some((Some(0x22), 0x30)));
        assert_eq!(designation_of(54), Some((Some(0x23), 0x36)));
        assert_eq!(designation_of(55), None);
    }

    #[test]
    fn designations_that_are_not_sets() {
        assert_eq!(private_set_number(&[0x23], 0x37), None, "number 55");
        assert_eq!(private_set_number(&[0x23], 0x3F), None, "number 63");
        assert_eq!(private_set_number(&[0x20], 0x30), None, "the SELECT-DRCS indicator");
        assert_eq!(private_set_number(&[0x21, 0x21], 0x30), None, "a third intermediate");
        assert_eq!(private_set_number(&[0x24], 0x30), None, "a supplement past 2/3");
        assert_eq!(private_set_number(&[], 0x42), None, "a registered final");
    }
}

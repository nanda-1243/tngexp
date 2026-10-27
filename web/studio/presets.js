/* MagPress magnet studio: ready-made combinations (cat 'preset').

   A preset has no draw(); it sets the frame, background pattern, whether the user's photo is used, the three
   colours and up to four marks (signature, date, brand, caption) with their positions. Rules kept here:
   one mark per corner / edge position, captions centred or at the top / bottom, light text over photos,
   and on the polaroid frame the caption (or date) sits in its deep bottom border.
*/
(function(){
  'use strict';
  const W = '#ffffff';
  const reg = (id, name, set) => MS.register({ id: 'preset.' + id, cat: 'preset', name, set });

  // ---------- minimal: photo with only an outline ----------
  reg('minimal-keyline', 'Minimal keyline', { photo: true, frame: 'frame.keyline', pattern: null,
    colors: { ink: '#1f1f1f', accent: '#1f1f1f', paper: '#ffffff' } });
  reg('gallery-matte', 'Gallery matte', { photo: true, frame: 'frame.matte', pattern: null,
    colors: { ink: '#2b2b2b', accent: '#8a7f72', paper: '#f7f3ec' } });
  reg('soft-vignette', 'Soft vignette', { photo: true, frame: 'frame.vignette', pattern: null,
    colors: { ink: '#1b1b1b', accent: '#c2410c', paper: '#ffffff' } });

  // ---------- wedding / anniversary / save the date ----------
  reg('wedding-names', 'Wedding names', { photo: true, frame: 'frame.double', pattern: null,
    colors: { ink: '#4a3a2e', accent: '#c9a227', paper: '#fffaf3' },
    signature: { style: 'signature.elegant', pos: 'bc', color: W },
    date: { style: 'date.serif', pos: 'tc', color: W, size: 0.85 } });
  reg('wedding-gold', 'Gold foil wedding', { photo: true, frame: 'frame.gold-foil', pattern: null,
    colors: { ink: '#3d2f1f', accent: '#c9a227', paper: '#fffdf7' },
    signature: { style: 'signature.script', pos: 'bc', color: W } });
  reg('anniversary-hearts', 'Anniversary hearts', { photo: true, frame: 'frame.hearts', pattern: null,
    colors: { ink: '#4a1c2c', accent: '#c2185b', paper: '#fff5f7' },
    caption: { style: 'caption.script', pos: 'tc', text: 'Happy Anniversary', size: 0.75 },
    date: { style: 'date.ribbon', pos: 'bc' } });
  reg('save-the-date', 'Save the date (marble)', { photo: false, frame: 'frame.double', pattern: 'pattern.marble',
    colors: { ink: '#2f2a24', accent: '#b8932f', paper: '#fbfaf6' },
    caption: { style: 'caption.title', pos: 'tc', text: 'Save the Date', size: 0.85 },
    signature: { style: 'signature.elegant', pos: 'mc', color: '#2f2a24' },
    date: { style: 'date.serif', pos: 'bc', color: '#8a6d1f' } });
  reg('save-the-date-photo', 'Save the date photo', { photo: true, frame: 'frame.inner-rounded', pattern: null,
    colors: { ink: '#3b2f2f', accent: '#d4a5a5', paper: '#fffaf7' },
    caption: { style: 'caption.script', pos: 'tc', text: 'Save the Date', color: W },
    date: { style: 'date.calendar', pos: 'bc' } });

  // ---------- birthday / baby / kids ----------
  reg('birthday-confetti', 'Birthday confetti', { photo: true, frame: 'frame.confetti', pattern: null,
    colors: { ink: '#2d2a4a', accent: '#ff6f3c', paper: '#fffaf0' },
    caption: { style: 'caption.banner', pos: 'bc', text: 'Happy Birthday' } });
  reg('birthday-balloons', 'Birthday balloons', { photo: false, frame: null, pattern: 'pattern.balloons',
    colors: { ink: '#2d2a4a', accent: '#ff5d8f', paper: '#fffaf3' },
    caption: { style: 'caption.bold', pos: 'mc', text: 'Happy Birthday' },
    signature: { style: 'signature.marker', pos: 'bc', color: '#e0457b' } });
  reg('new-arrival', 'New arrival', { photo: true, frame: 'frame.polaroid', pattern: null,
    colors: { ink: '#34506b', accent: '#8ec5e8', paper: '#ffffff' },
    caption: { style: 'caption.script', pos: 'bc', text: 'Welcome Baby', size: 0.9 } });
  reg('baby-birth-date', 'Baby birth date', { photo: true, frame: 'frame.dots', pattern: null,
    colors: { ink: '#5b4b6b', accent: '#f4b6c2', paper: '#fff9fb' },
    signature: { style: 'signature.handwritten', pos: 'bc', color: W },
    date: { style: 'date.minimal', pos: 'tc', color: W } });
  reg('kids-name', 'Kid\'s name', { photo: false, frame: 'frame.ring', pattern: 'pattern.stars',
    colors: { ink: '#264653', accent: '#f4a300', paper: '#fff8e7' },
    caption: { style: 'caption.bold', pos: 'mc', text: 'AARAV', size: 1.8 } });

  // ---------- travel / camera / film ----------
  reg('travel-postcard', 'Travel postcard', { photo: true, frame: 'frame.stamp', pattern: null,
    colors: { ink: '#3d2c1e', accent: '#1f7a8c', paper: '#fdf6e3' },
    caption: { style: 'caption.bold', pos: 'bc', text: 'Greetings from Goa', color: W },
    date: { style: 'date.postmark', pos: 'tr' } });
  reg('retro-camera', 'Retro camera date', { photo: true, frame: 'frame.keyline', pattern: null,
    colors: { ink: '#1f1f1f', accent: '#ff8a1e', paper: '#ffffff' },
    date: { style: 'date.camera', pos: 'br', color: '#ff9a2e' } });
  reg('film-roll', 'Film roll', { photo: true, frame: 'frame.filmstrip', pattern: null,
    colors: { ink: '#141414', accent: '#e8b04a', paper: '#ffffff' } });
  reg('torn-journal', 'Travel journal', { photo: true, frame: 'frame.torn', pattern: null,
    colors: { ink: '#3a3226', accent: '#a0522d', paper: '#fbf6ea' },
    caption: { style: 'caption.script', pos: 'tc', text: 'Wanderlust', color: W },
    date: { style: 'date.typewriter', pos: 'bc', color: W } });
  reg('polaroid-memories', 'Polaroid memories', { photo: true, frame: 'frame.polaroid', pattern: null,
    colors: { ink: '#2b2b2b', accent: '#c2410c', paper: '#fdfdfb' },
    date: { style: 'date.typewriter', pos: 'bc', color: '#444444' } });

  // ---------- festivals / holidays ----------
  reg('festival-lights', 'Festival of lights', { photo: false, frame: 'frame.gold-foil', pattern: 'pattern.bokeh',
    colors: { ink: '#fff3d6', accent: '#f2b134', paper: '#1a1440' },
    caption: { style: 'caption.script', pos: 'mc', text: 'Happy Diwali', color: '#ffe3a3' },
    signature: { style: 'signature.with-love', pos: 'bc', color: '#fff3d6' } });
  reg('rangoli', 'Rangoli greetings', { photo: false, frame: null, pattern: 'pattern.mandala',
    colors: { ink: '#7a1f3d', accent: '#e4572e', paper: '#fff6e5' },
    caption: { style: 'caption.banner', pos: 'mc', text: 'Happy Pongal' } });
  reg('christmas-wreath', 'Christmas wreath', { photo: true, frame: 'frame.wreath', pattern: null,
    colors: { ink: '#1e4d2b', accent: '#b3202a', paper: '#fffaf0' },
    caption: { style: 'caption.script', pos: 'bc', text: 'Merry Christmas', color: W, size: 0.7 } });
  reg('christmas-stars', 'Christmas stars', { photo: false, frame: 'frame.dots', pattern: 'pattern.stars',
    colors: { ink: '#fff8ec', accent: '#e9c46a', paper: '#1e4d2b' },
    caption: { style: 'caption.title', pos: 'mc', text: 'Merry Christmas', color: '#fff8ec' } });
  reg('neon-party', 'Neon party', { photo: true, frame: 'frame.neon', pattern: null,
    colors: { ink: '#ffffff', accent: '#ff3fa4', paper: '#160a2b' },
    caption: { style: 'caption.bold', pos: 'tc', text: 'Let\'s Party', color: W } });

  // ---------- graduation / pets / thanks / quote ----------
  reg('graduation', 'Graduation', { photo: true, frame: 'frame.double', pattern: null,
    colors: { ink: '#0f2340', accent: '#c9a227', paper: '#ffffff' },
    caption: { style: 'caption.bold', pos: 'tc', text: 'Class of 2026', color: W },
    signature: { style: 'signature.marker', pos: 'bc', color: W } });
  reg('pet-portrait', 'Pet portrait', { photo: true, frame: 'frame.inner-rounded', pattern: null,
    colors: { ink: '#3d405b', accent: '#e07a5f', paper: '#fdf3e7' },
    signature: { style: 'signature.handwritten', pos: 'bc', color: W } });
  reg('pet-paws', 'Paw prints', { photo: false, frame: 'frame.keyline', pattern: 'pattern.paws',
    colors: { ink: '#3d405b', accent: '#e07a5f', paper: '#fdf3e7' },
    caption: { style: 'caption.bold', pos: 'mc', text: 'Woof!', size: 1.4 },
    signature: { style: 'signature.marker', pos: 'bc', color: '#c4573e' } });
  reg('thank-you', 'Thank you', { photo: false, frame: null, pattern: 'pattern.floral',
    colors: { ink: '#5d4037', accent: '#e5989b', paper: '#fffaf7' },
    caption: { style: 'caption.script', pos: 'mc', text: 'Thank You' },
    brand: { style: 'brand.wordmark', pos: 'bc' } });
  reg('quote', 'Quote', { photo: false, frame: 'frame.ornate', pattern: 'pattern.gradient',
    colors: { ink: '#23395b', accent: '#7aa6c2', paper: '#ffffff' },
    caption: { style: 'caption.quote', pos: 'mc', text: 'Collect moments, not things', size: 1.6 } });

  // ---------- brand / business ----------
  reg('brand-promo', 'Brand promo', { photo: true, frame: 'frame.keyline', pattern: null,
    colors: { ink: '#111827', accent: '#0f766e', paper: '#ffffff' },
    brand: { style: 'brand.corner-tag', pos: 'tr' },
    caption: { style: 'caption.banner', pos: 'bc', text: 'Grand Opening' } });
  reg('photographer', 'Photographer\'s mark', { photo: true, frame: 'frame.keyline', pattern: null,
    colors: { ink: '#1f1f1f', accent: '#1f1f1f', paper: '#ffffff' },
    brand: { style: 'brand.copyright', pos: 'br', color: W },
    date: { style: 'date.minimal', pos: 'bl', color: W } });
  reg('event-keepsake', 'Event keepsake', { photo: true, frame: 'frame.gold-foil', pattern: null,
    colors: { ink: '#3d2f1f', accent: '#c9a227', paper: '#fffdf7' },
    date: { style: 'date.minimal', pos: 'tl', color: W },
    brand: { style: 'brand.copyright', pos: 'tr', color: W },
    signature: { style: 'signature.script', pos: 'bc', color: W } });
  reg('shop-sale', 'Shop event', { photo: true, frame: 'frame.ring', pattern: null,
    colors: { ink: '#1f2937', accent: '#e11d48', paper: '#ffffff' },
    brand: { style: 'brand.stamp', pos: 'tl' },
    date: { style: 'date.calendar', pos: 'br' } });
  reg('business-card', 'Business card', { photo: false, frame: 'frame.double', pattern: null,
    colors: { ink: '#292524', accent: '#b45309', paper: '#f7f4ee' },
    brand: { style: 'brand.wordmark', pos: 'mc', size: 1.9 },
    caption: { style: 'caption.title', pos: 'bc', text: 'www.yourshop.in', size: 0.5 } });
  reg('brand-seal', 'Brand seal', { photo: false, frame: 'frame.ring', pattern: 'pattern.terrazzo',
    colors: { ink: '#1f2a2e', accent: '#d9825b', paper: '#faf6f0' },
    brand: { style: 'brand.seal', pos: 'mc' } });
})();

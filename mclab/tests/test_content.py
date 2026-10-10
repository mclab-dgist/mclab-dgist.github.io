"""Regression tests use temporary fixtures; new user records do not break fixed counts."""
import base64
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_site',ROOT/'scripts/build_site.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aXioAAAAASUVORK5CYII=')

class ContentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        for cat in b.CATEGORIES:(self.root/'content'/cat).mkdir(parents=True)
        base={'config':{},'pi':{'interests':[]},'research':[],'news':[],'gallery':[],'recruitment':{},'sources':{}}
        (self.root/'content/site.json').write_text(json.dumps(base))
        self.person('faculty',group='Faculty',role='Professor')
        for name in b.PAGES:(self.root/(name+'.html')).write_text('<!doctype html><title>Fixture</title>')
        (self.root/'assets').mkdir()
    def tearDown(self):self.tmp.cleanup()
    def put(self,cat,slug,data):
        p=self.root/'content'/cat/slug;p.mkdir(exist_ok=True)
        (p/'info.json').write_text(json.dumps({'id':slug,**data},ensure_ascii=False),encoding='utf-8')
        return p
    def person(self,slug='student',**kw):
        return self.put('people',slug,{'name':'Test Student','group':'M.S. students','role':'M.S. Student','visible':True,**kw})
    def paper(self,slug='paper',**kw):
        return self.put('publications',slug,{'title':'Test Title','authors':'A. Student and K. H. Nam','venue':'Test Journal','status':'Published','year':2026,**kw})
    def project(self,slug='project',**kw):
        return self.put('projects',slug,{'title':'Test Project','funder':'Test Funder','category':'Industry','start':'2026-01','end':'2026-12',**kw})
    def collect(self):return b.collect(self.root,'2026-10-10')
    def test_txt_and_bom(self):
        p=self.root/'info.txt';p.write_text('\ufeff이름: Test\n과정: 석사과정\n분류: 석사과정\n',encoding='utf-8')
        self.assertEqual(b.read_info(p)['name'],'Test')
    def test_multiline(self):
        p=self.root/'info.txt';p.write_text('요약: |\n  Line 1\n  Line 2\n링크: https://example.org/a:b\n',encoding='utf-8')
        self.assertEqual(b.read_info(p)['summary'],'Line 1\nLine 2')
    def test_duplicate_keys(self):
        p=self.root/'info.txt';p.write_text('이름: X\nname: Y',encoding='utf-8')
        with self.assertRaises(b.ContentError):b.read_info(p)
    def test_duplicate_json(self):
        p=self.root/'info.json';p.write_text('{"name":"A","name":"B"}')
        with self.assertRaises(b.ContentError):b.read_info(p)
    def test_unknown_key_rejected(self):
        self.person(typo_visibility='false')
        with self.assertRaises(b.ContentError):self.collect()
    def test_boolean_typo_rejected(self):
        self.person(visible='flase')
        with self.assertRaises(b.ContentError):self.collect()
    def test_add_modify_hide_delete(self):
        p=self.person();self.assertEqual(len(self.collect()[0]['people']),1)
        self.person(name='Updated Name');self.assertEqual(self.collect()[0]['people'][0]['name'],'Updated Name')
        self.person(visible=False);self.assertEqual(len(self.collect()[0]['people']),0)
        (p/'info.json').unlink();p.rmdir();self.assertEqual(len(self.collect()[0]['people']),0)
    def test_korean_enum(self):
        self.person(group='박사과정',role='박사과정');r=self.collect()[0]['people'][0]
        self.assertEqual(r['group'],'Ph.D. students');self.assertEqual(r['role'],'Ph.D. Student')
    def test_missing_required_info(self):
        self.person(name='')
        with self.assertRaises(b.ContentError):self.collect()
    def test_photo_autolink_and_hash(self):
        p=self.person();(p/'photo.png').write_bytes(PNG)
        u=self.collect()[0]['people'][0]['photo'];self.assertTrue(u.startswith('media/people/student/'))
        (p/'photo.png').write_bytes(PNG+b'changed');v=self.collect()[0]['people'][0]['photo'];self.assertNotEqual(u,v)
    def test_ambiguous_photos_fail(self):
        p=self.person();(p/'photo.png').write_bytes(PNG);(p/'photo.jpg').write_bytes(b'\xff\xd8\xfftest')
        with self.assertRaises(b.ContentError):self.collect()
    def test_missing_explicit_photo_fails(self):
        self.person(photo='missing.png')
        with self.assertRaises(b.ContentError):self.collect()
    def test_path_traversal_rejected(self):
        self.person(photo='../secret.png')
        with self.assertRaises(b.ContentError):self.collect()
    def test_script_url_rejected(self):
        self.person(website='javascript:alert(1)')
        with self.assertRaises(b.ContentError):self.collect()
    def test_mislabelled_image(self):
        p=self.person();(p/'photo.png').write_text('<html>not an image</html>')
        with self.assertRaises(b.ContentError):self.collect()
    def test_published_year_required(self):
        self.paper(year='')
        with self.assertRaises(b.ContentError):self.collect()
    def test_accepted_does_not_become_published(self):
        self.paper(status='게재확정',year='');r=self.collect()[0]['publications'][0]
        self.assertEqual(r['status'],'Accepted');self.assertIsNone(r['year'])
    def test_doi_normalization_and_duplicate(self):
        self.paper(doi='https://doi.org/10.1234/example');self.assertEqual(self.collect()[0]['publications'][0]['doi'],'10.1234/example')
        self.paper('second-paper',doi='10.1234/EXAMPLE')
        with self.assertRaises(b.ContentError):self.collect()
    def test_pdf_only_not_interpreted(self):
        p=self.root/'content/publications/orphan';p.mkdir();(p/'paper.pdf').write_bytes(b'%PDF-1.7 fixture')
        with self.assertRaises(b.ContentError):self.collect()
    def test_only_public_linked_assets_deployed(self):
        p=self.paper();(p/'paper.pdf').write_bytes(b'%PDF-1.7\n% Fixture only\n%%EOF')
        (p/'contract.txt').write_text('DO NOT PUBLISH')
        hidden=self.person(visible=False);(hidden/'photo.png').write_bytes(PNG)
        with contextlib.redirect_stdout(io.StringIO()):report=b.build(self.root,self.root/'_site','2026-10-10')
        self.assertEqual(report['linkedAssets'],1)
        self.assertFalse((self.root/'_site/content').exists())
        self.assertFalse(any(p.name=='contract.txt' for p in (self.root/'_site').rglob('*')))
        self.assertFalse(any('photo' in p.name for p in (self.root/'_site').rglob('*')))
    def test_dates_and_month_boundaries(self):
        self.assertEqual(b.project_status('2026-10','2026-10','2026-09-30'),'Upcoming')
        self.assertEqual(b.project_status('2026-10','2026-10','2026-10-31'),'Ongoing')
        self.assertEqual(b.project_status('2026-10','2026-10','2026-11-01'),'Completed')
        self.assertEqual(b.project_status('2026-10-10','2026-10-10','2026-10-11'),'Completed')
    def test_invalid_project_dates(self):
        self.project(start='2026-12',end='2026-11')
        with self.assertRaises(b.ContentError):self.collect()
    def test_manual_project_status(self):
        self.project(status='On hold');r=self.collect()[0]['projects'][0]
        self.assertEqual(r['status'],'On hold');self.assertEqual(r['statusMode'],'On hold')
    def test_filename_id_consistency(self):
        self.person(id='different-id')
        with self.assertRaises(b.ContentError):self.collect()
    def test_html_data_escaped(self):
        js=b.js_data({'title':'</script><script>alert(1)</script>'})
        self.assertNotIn('</script>',js)
        self.assertIn('\\u003c',js)
    def test_failed_build_preserves_previous_output(self):
        out=self.root/'_site';out.mkdir();(out/'sentinel.txt').write_text('old website')
        self.person(name='')
        with self.assertRaises(b.ContentError):b.build(self.root,out,'2026-10-10')
        self.assertEqual((out/'sentinel.txt').read_text(),'old website')
    def test_output_guard(self):
        with self.assertRaises(b.ContentError):b.build(self.root,self.root,'2026-10-10')
    def test_repository_current_content_valid(self):
        data,_,report=b.collect(ROOT,'2026-10-10')
        self.assertEqual(report['faculty'],1)
        years=[p['year'] or 0 for p in data['publications']]
        self.assertEqual(years,sorted(years,reverse=True))

    def test_publication_source_notes_preserved(self):
        self.paper(sourceRanking='JCR Q2',sourceCitation='Original citation',note='Check pages',source='https://example.org')
        r=self.collect()[0]['publications'][0]
        self.assertEqual(r['sourceRanking'],'JCR Q2')
        self.assertEqual(r['sourceCitation'],'Original citation')
    def test_invalid_source_url_rejected(self):
        self.paper(source='javascript:alert(1)')
        with self.assertRaises(b.ContentError):self.collect()
    def extra(self,folder,slug,data):
        parent=self.root/'content'/folder;parent.mkdir(exist_ok=True)
        return self.put(folder,slug,data)
    def test_news_folder_loaded_and_photo_linked(self):
        p=self.extra('news','test-news',{'date':'2026-10-10','title':'Test','text':'Text'})
        (p/'photo.png').write_bytes(PNG)
        r=self.collect()[0]['news'][0]
        self.assertTrue(r['image'].startswith('media/news/'))
        self.assertEqual(r['date'],'2026-10-10')
    def test_news_month_without_day_rejected(self):
        self.extra('news','test-news',{'date':'2026-10','title':'Test','text':'Text'})
        with self.assertRaises(b.ContentError):self.collect()
    def test_gallery_without_photo_rejected(self):
        self.extra('gallery','test-photo',{'title':'Test'})
        with self.assertRaises(b.ContentError):self.collect()
    def test_undated_gallery_with_photo_allowed(self):
        p=self.extra('gallery','test-photo',{'title':'Test'})
        (p/'photo.png').write_bytes(PNG)
        self.assertEqual(self.collect()[0]['gallery'][0]['date'],'')
    def test_hidden_news_is_not_deployed(self):
        self.extra('news','test-news',{'visible':False,'title':'Draft'})
        self.assertEqual(self.collect()[0]['news'],[])
    def test_research_program_checked(self):
        self.extra('research','test-topic',{'program':'missing','title':'Test','description':'Test'})
        with self.assertRaises(b.ContentError):self.collect()
    def test_extra_assets_only_in_pages_artifact(self):
        p=self.extra('gallery','test-photo',{'title':'Test'})
        (p/'photo.png').write_bytes(PNG)
        (p/'secret.txt').write_text('not for the site')
        with contextlib.redirect_stdout(io.StringIO()):b.build(self.root,self.root/'_site','2026-10-10')
        self.assertTrue(any(x.suffix=='.png' for x in (self.root/'_site/media').rglob('*')))
        self.assertFalse((self.root/'_site/content').exists())

if __name__=='__main__':unittest.main()

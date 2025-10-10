"""Tests for markdown_updater module."""

from pathlib import Path
from tempfile import TemporaryDirectory

from notes_cli.markdown_updater import update_markdown_files


class TestMarkdownLinkUpdating:
    """Test updating various markdown link formats."""

    def test_simple_uploads_prefix(self) -> None:
        """Test updating links with uploads/ prefix."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("![image](uploads/original.png)", encoding="utf-8")

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "uploads/optimized.png" in content
            assert "uploads/original.png" not in content

    def test_simple_relative_uploads_prefix(self) -> None:
        """Test updating links with ./uploads/ prefix."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("![image](./uploads/original.png)", encoding="utf-8")

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "uploads/optimized.png" in content
            assert "./uploads/original.png" not in content

    def test_simple_absolute_uploads_prefix(self) -> None:
        """Test updating links with /uploads/ prefix."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("![image](/uploads/original.png)", encoding="utf-8")

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "/uploads/optimized.png" in content
            assert "/uploads/original.png" not in content

    def test_wiki_style_link_without_display_name(self) -> None:
        """Test updating Obsidian wiki-style links without display names."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("[[original.png]]", encoding="utf-8")

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "[[uploads/optimized.png]]" in content
            assert "[[original.png]]" not in content

    def test_wiki_style_image_link_without_display_name(self) -> None:
        """Test updating Obsidian wiki-style image links (![[...]]) without display names."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("![[original.png]]", encoding="utf-8")

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "![[uploads/optimized.png]]" in content
            assert "![[original.png]]" not in content

    def test_wiki_style_link_with_display_name(self) -> None:
        """Test updating wiki-style links with display names, preserving the display name."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("[[original.png|My Image]]", encoding="utf-8")

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "[[uploads/optimized.png|My Image]]" in content
            assert "[[original.png|My Image]]" not in content

    def test_wiki_style_image_link_with_display_name(self) -> None:
        """Test updating wiki-style image links with display names."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("![[original.png|My Image]]", encoding="utf-8")

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "![[uploads/optimized.png|My Image]]" in content
            assert "![[original.png|My Image]]" not in content

    def test_standard_markdown_without_uploads_prefix(self) -> None:
        """Test updating standard markdown images without uploads/ prefix."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("![alt text](original.png)", encoding="utf-8")

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "![alt text](uploads/optimized.png)" in content
            assert "(original.png)" not in content

    def test_multiple_references_in_same_file(self) -> None:
        """Test updating multiple references to the same image in one file."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text(
                "![img1](original.png)\n[[original.png]]\n![[original.png]]",
                encoding="utf-8",
            )

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "![img1](uploads/optimized.png)" in content
            assert "[[uploads/optimized.png]]" in content
            assert "![[uploads/optimized.png]]" in content
            assert "original.png" not in content

    def test_mixed_link_formats(self) -> None:
        """Test updating a file with mixed link formats."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text(
                "![image](uploads/img1.png)\n"
                "[[img2.png|Display]]\n"
                "![[img3.png]]\n"
                "![another](./uploads/img4.png)",
                encoding="utf-8",
            )

            img1_orig = tmpdir_path / "img1.png"
            img1_opt = tmpdir_path / "img1-opt.png"
            img2_orig = tmpdir_path / "img2.png"
            img2_opt = tmpdir_path / "img2-opt.png"
            img3_orig = tmpdir_path / "img3.png"
            img3_opt = tmpdir_path / "img3-opt.png"
            img4_orig = tmpdir_path / "img4.png"
            img4_opt = tmpdir_path / "img4-opt.png"

            update_markdown_files(
                [
                    (img1_orig, img1_opt, [md_file]),
                    (img2_orig, img2_opt, [md_file]),
                    (img3_orig, img3_opt, [md_file]),
                    (img4_orig, img4_opt, [md_file]),
                ],
                dry_run=False,
            )

            content = md_file.read_text(encoding="utf-8")
            assert "uploads/img1-opt.png" in content
            assert "[[uploads/img2-opt.png|Display]]" in content
            assert "![[uploads/img3-opt.png]]" in content
            assert "uploads/img4-opt.png" in content

    def test_no_update_when_names_are_same(self) -> None:
        """Test that no update occurs when original and optimized names are the same."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            original_content = "![image](uploads/same.png)"
            md_file.write_text(original_content, encoding="utf-8")

            same_path = tmpdir_path / "same.png"

            files_updated, refs_updated = update_markdown_files(
                [(same_path, same_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert content == original_content
            assert files_updated == 0
            assert refs_updated == 0

    def test_dry_run_mode(self) -> None:
        """Test that dry run mode doesn't actually update files."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            original_content = "![image](original.png)"
            md_file.write_text(original_content, encoding="utf-8")

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            files_updated, refs_updated = update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=True
            )

            content = md_file.read_text(encoding="utf-8")
            assert content == original_content
            assert refs_updated == 1  # Should count the reference
            assert files_updated == 0  # But not update files

    def test_preserves_unrelated_content(self) -> None:
        """Test that unrelated content in markdown is preserved."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text(
                "# Header\n\nSome text\n\n![image](original.png)\n\nMore text\n\n"
                "- List item 1\n- List item 2",
                encoding="utf-8",
            )

            original_path = tmpdir_path / "original.png"
            optimized_path = tmpdir_path / "optimized.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "# Header" in content
            assert "Some text" in content
            assert "More text" in content
            assert "- List item 1" in content
            assert "- List item 2" in content
            assert "uploads/optimized.png" in content

    def test_special_characters_in_filename(self) -> None:
        """Test updating links with special characters in filenames."""
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test.md"
            md_file.write_text("![image](my-image_2024(1).png)", encoding="utf-8")

            original_path = tmpdir_path / "my-image_2024(1).png"
            optimized_path = tmpdir_path / "my-image_2024(1)-opt.png"

            update_markdown_files(
                [(original_path, optimized_path, [md_file])], dry_run=False
            )

            content = md_file.read_text(encoding="utf-8")
            assert "uploads/my-image_2024(1)-opt.png" in content
